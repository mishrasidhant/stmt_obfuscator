#!/usr/bin/env python3
"""
Test Data Generator for PDF Bank Statement Obfuscator.

This module provides utilities for generating diverse synthetic bank statement
samples for testing purposes, with ground truth annotations for PII entities.
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

from faker import Faker
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Import the BankStatementGenerator from the POC for compatibility
try:
    from pii_detection_poc.scripts.generate_samples import BankStatementGenerator as POCGenerator
except ImportError:
    POCGenerator = None


class StatementFormat:
    """Defines different bank statement formats for testing."""
    
    FORMATS = {
        "standard": {
            "header_style": "centered",
            "account_info_style": "table",
            "transaction_style": "table",
            "footer_style": "simple",
            "font_name": "Helvetica",
            "has_logo": False,
            "has_tables": True,
            "has_summary": True,
        },
        "minimal": {
            "header_style": "simple",
            "account_info_style": "inline",
            "transaction_style": "simple",
            "footer_style": "none",
            "font_name": "Courier",
            "has_logo": False,
            "has_tables": False,
            "has_summary": False,
        },
        "modern": {
            "header_style": "logo",
            "account_info_style": "boxed",
            "transaction_style": "alternating",
            "footer_style": "detailed",
            "font_name": "Helvetica-Bold",
            "has_logo": True,
            "has_tables": True,
            "has_summary": True,
        },
        "detailed": {
            "header_style": "detailed",
            "account_info_style": "detailed",
            "transaction_style": "detailed",
            "footer_style": "detailed",
            "font_name": "Times-Roman",
            "has_logo": True,
            "has_tables": True,
            "has_summary": True,
        }
    }
    
    @classmethod
    def get_format(cls, format_name: str) -> Dict:
        """Get a statement format by name."""
        return cls.FORMATS.get(format_name, cls.FORMATS["standard"])
    
    @classmethod
    def get_random_format(cls) -> Dict:
        """Get a random statement format."""
        return random.choice(list(cls.FORMATS.values()))


class PIIDistribution:
    """Defines different PII distribution patterns for testing."""
    
    DISTRIBUTIONS = {
        "standard": {
            "person_name": 1.0,
            "address": 1.0,
            "account_number": 1.0,
            "routing_number": 1.0,
            "phone_number": 1.0,
            "email": 1.0,
            "organization_name": 1.0,
            "website": 1.0,
            "ssn": 0.3,
            "credit_card": 0.3,
            "ip_address": 0.1,
        },
        "minimal": {
            "person_name": 1.0,
            "account_number": 1.0,
            "routing_number": 0.5,
            "address": 0.5,
            "phone_number": 0.2,
            "email": 0.0,
            "organization_name": 1.0,
            "website": 0.0,
            "ssn": 0.0,
            "credit_card": 0.0,
            "ip_address": 0.0,
        },
        "heavy": {
            "person_name": 1.0,
            "address": 1.0,
            "account_number": 1.0,
            "routing_number": 1.0,
            "phone_number": 1.0,
            "email": 1.0,
            "organization_name": 1.0,
            "website": 1.0,
            "ssn": 0.8,
            "credit_card": 0.8,
            "ip_address": 0.5,
            "additional_names": 3,  # Additional person names in transactions
        },
    }
    
    @classmethod
    def get_distribution(cls, distribution_name: str) -> Dict:
        """Get a PII distribution by name."""
        return cls.DISTRIBUTIONS.get(distribution_name, cls.DISTRIBUTIONS["standard"])
    
    @classmethod
    def get_random_distribution(cls) -> Dict:
        """Get a random PII distribution."""
        return random.choice(list(cls.DISTRIBUTIONS.values()))


class EnhancedBankStatementGenerator:
    """
    An enhanced generator for creating diverse synthetic bank statements with ground truth annotations.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the EnhancedBankStatementGenerator.

        Args:
            seed: Random seed for reproducibility (default: None)
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
            
        # Bank names for generating realistic statements
        self.bank_names = [
            "First National Bank",
            "Capital One",
            "Chase Bank",
            "Bank of America",
            "Wells Fargo",
            "Citibank",
            "TD Bank",
            "PNC Bank",
            "US Bank",
            "Truist Bank",
            "Ally Bank",
            "Discover Bank",
            "HSBC Bank",
            "Santander Bank",
            "Fifth Third Bank",
            "KeyBank",
            "Regions Bank",
            "SunTrust Bank",
            "BB&T Bank",
            "Citizens Bank",
        ]
        
        # Transaction descriptions for generating realistic statements
        self.transaction_types = [
            "PURCHASE", "PAYMENT", "DEPOSIT", "WITHDRAWAL", "TRANSFER", 
            "ATM WITHDRAWAL", "CHECK", "DIRECT DEPOSIT", "INTEREST", "FEE",
            "REFUND", "CREDIT", "DEBIT", "ONLINE PAYMENT", "SUBSCRIPTION",
            "RECURRING PAYMENT", "BILL PAYMENT", "CASH ADVANCE", "WIRE TRANSFER",
            "MOBILE DEPOSIT", "VENMO", "PAYPAL", "ZELLE", "CASH APP"
        ]
        
        self.merchants = [
            "AMAZON", "WALMART", "TARGET", "COSTCO", "KROGER", "STARBUCKS", 
            "UBER", "NETFLIX", "SPOTIFY", "APPLE", "GOOGLE", "MICROSOFT",
            "HOME DEPOT", "LOWES", "BEST BUY", "MCDONALDS", "CHIPOTLE",
            "SHELL", "EXXON", "CHEVRON", "DELTA", "AMERICAN AIRLINES",
            "HILTON", "MARRIOTT", "AIRBNB", "DOORDASH", "GRUBHUB", "INSTACART",
            "CVS", "WALGREENS", "RITE AID", "TRADER JOES", "WHOLE FOODS",
            "SUBWAY", "BURGER KING", "WENDYS", "TACO BELL", "KFC",
            "DISNEY+", "HULU", "HBO MAX", "AMAZON PRIME", "YOUTUBE PREMIUM",
            "VERIZON", "AT&T", "T-MOBILE", "COMCAST", "SPECTRUM", "COX",
            "ADOBE", "MICROSOFT 365", "DROPBOX", "SLACK", "ZOOM", "GITHUB"
        ]
        
        # Credit card types
        self.credit_card_types = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]
        
        # Statement formats
        self.statement_formats = list(StatementFormat.FORMATS.keys())
        
        # PII distributions
        self.pii_distributions = list(PIIDistribution.DISTRIBUTIONS.keys())

    def generate_statement(self, 
                          format_name: Optional[str] = None, 
                          pii_distribution_name: Optional[str] = None,
                          num_transactions: Optional[int] = None,
                          include_pdf: bool = False,
                          output_dir: Optional[str] = None) -> Tuple[str, Dict, Optional[str]]:
        """
        Generate a synthetic bank statement with ground truth annotations.

        Args:
            format_name: Name of the statement format to use (default: random)
            pii_distribution_name: Name of the PII distribution to use (default: random)
            num_transactions: Number of transactions to generate (default: random between 10-30)
            include_pdf: Whether to generate a PDF version of the statement (default: False)
            output_dir: Directory to save the PDF file (default: None)

        Returns:
            A tuple containing:
                - The generated bank statement text
                - A dictionary with ground truth PII annotations
                - Path to the generated PDF file (if include_pdf is True, otherwise None)
        """
        # Select format and PII distribution
        if format_name is None:
            format_name = random.choice(self.statement_formats)
        
        if pii_distribution_name is None:
            pii_distribution_name = random.choice(self.pii_distributions)
            
        if num_transactions is None:
            num_transactions = random.randint(10, 30)
            
        statement_format = StatementFormat.get_format(format_name)
        pii_distribution = PIIDistribution.get_distribution(pii_distribution_name)
        
        # Generate customer information
        customer = self._generate_customer_info(pii_distribution)
        
        # Generate bank information
        bank = self._generate_bank_info(pii_distribution)
        
        # Generate statement period
        end_date = datetime.now().replace(day=random.randint(1, 28))
        start_date = end_date - timedelta(days=30)
        
        # Generate transactions
        transactions = self._generate_transactions(
            start_date, 
            end_date, 
            num_transactions, 
            pii_distribution
        )
        
        # Generate the statement text
        statement_text = self._generate_statement_text(
            customer, 
            bank, 
            start_date, 
            end_date, 
            transactions,
            statement_format
        )
        
        # Generate ground truth annotations
        ground_truth = self._generate_ground_truth(statement_text, customer, bank)
        
        # Generate PDF if requested
        pdf_path = None
        if include_pdf:
            pdf_path = self._generate_pdf(
                customer,
                bank,
                start_date,
                end_date,
                transactions,
                statement_format,
                output_dir
            )
        
        return statement_text, ground_truth, pdf_path

    def _generate_customer_info(self, pii_distribution: Dict) -> Dict:
        """Generate customer information based on PII distribution."""
        customer = {
            "name": self.faker.name(),
            "address": self.faker.address().replace('\n', ', '),
            "account_number": f"{random.randint(10000000, 99999999)}",
            "routing_number": f"{random.randint(100000000, 999999999)}",
            "phone": self.faker.phone_number(),
            "email": self.faker.email(),
            "ssn_last4": f"{random.randint(1000, 9999)}"
        }
        
        # Add full SSN if in distribution
        if random.random() < pii_distribution.get("ssn", 0):
            customer["ssn"] = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{customer['ssn_last4']}"
            
        # Add credit card if in distribution
        if random.random() < pii_distribution.get("credit_card", 0):
            cc_type = random.choice(self.credit_card_types)
            if cc_type == "AMEX":
                customer["credit_card"] = f"3{''.join([str(random.randint(0, 9)) for _ in range(14)])}"
            else:
                customer["credit_card"] = f"{'4' if cc_type == 'VISA' else '5' if cc_type == 'MASTERCARD' else '6'}{''.join([str(random.randint(0, 9)) for _ in range(15)])}"
                
        # Add IP address if in distribution
        if random.random() < pii_distribution.get("ip_address", 0):
            customer["ip_address"] = self.faker.ipv4()
            
        return customer

    def _generate_bank_info(self, pii_distribution: Dict) -> Dict:
        """Generate bank information based on PII distribution."""
        bank = {
            "name": random.choice(self.bank_names),
            "address": self.faker.address().replace('\n', ', '),
            "phone": self.faker.phone_number(),
            "website": f"www.{self.faker.domain_name()}"
        }
        
        return bank

    def _generate_transactions(self, 
                              start_date: datetime, 
                              end_date: datetime, 
                              num_transactions: int,
                              pii_distribution: Dict) -> List[Dict]:
        """Generate transactions based on PII distribution."""
        transactions = []
        
        balance = random.randint(1000, 10000)
        
        # Generate additional person names for transfers if specified
        additional_names = []
        if "additional_names" in pii_distribution:
            for _ in range(pii_distribution["additional_names"]):
                additional_names.append(self.faker.name())
        
        for _ in range(num_transactions):
            date = self.faker.date_between(start_date=start_date, end_date=end_date)
            amount = round(random.uniform(1, 500), 2)
            
            # Randomly decide if it's a debit or credit
            is_debit = random.random() < 0.7  # 70% chance of being a debit
            
            if is_debit:
                balance -= amount
                amount = -amount
            else:
                balance += amount
            
            transaction_type = random.choice(self.transaction_types)
            
            if transaction_type in ["PURCHASE", "PAYMENT"]:
                description = f"{transaction_type} - {random.choice(self.merchants)}"
            elif transaction_type == "DIRECT DEPOSIT":
                description = f"{transaction_type} - {self.faker.company()}"
            elif transaction_type == "TRANSFER":
                # Sometimes include another person's name in transfers
                if random.random() < 0.5 and additional_names:
                    other_person = random.choice(additional_names)
                    description = f"{transaction_type} {'TO' if is_debit else 'FROM'} {other_person}"
                else:
                    description = f"{transaction_type} {'TO' if is_debit else 'FROM'} ACCOUNT {random.randint(1000, 9999)}"
            else:
                description = transaction_type
            
            transactions.append({
                "date": date.strftime("%m/%d/%Y"),
                "description": description,
                "amount": amount,
                "balance": round(balance, 2)
            })
        
        # Sort transactions by date
        transactions.sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"))
        
        return transactions

    def _generate_statement_text(self, 
                                customer: Dict, 
                                bank: Dict, 
                                start_date: datetime, 
                                end_date: datetime, 
                                transactions: List[Dict],
                                statement_format: Dict) -> str:
        """Generate the bank statement text based on the specified format."""
        # Base statement structure
        statement = f"""
{bank['name']}
{bank['address']}
Phone: {bank['phone']}
Website: {bank['website']}

ACCOUNT STATEMENT

Statement Period: {start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}

CUSTOMER INFORMATION:
{customer['name']}
{customer['address']}
Phone: {customer['phone']}
Email: {customer['email']}
"""

        # Add SSN if present
        if "ssn" in customer:
            statement += f"SSN: {customer['ssn']}\n"
        
        # Add credit card if present
        if "credit_card" in customer:
            statement += f"Credit Card: {customer['credit_card']}\n"
            
        # Add IP address if present
        if "ip_address" in customer:
            statement += f"Last Login IP: {customer['ip_address']}\n"

        # Account summary section
        statement += f"""
ACCOUNT SUMMARY:
Account Number: XXXX-XXXX-XXXX-{customer['account_number'][-4:]}
Routing Number: {customer['routing_number']}
Beginning Balance: ${transactions[0]['balance'] - transactions[0]['amount']:.2f}
Ending Balance: ${transactions[-1]['balance']:.2f}
"""

        # Transaction history section
        statement += f"""
TRANSACTION HISTORY:
Date       Description                                Amount      Balance
----------------------------------------------------------------------------------
"""
        
        for transaction in transactions:
            date = transaction['date']
            description = transaction['description']
            amount = transaction['amount']
            balance = transaction['balance']
            
            # Format the transaction line
            statement += f"{date:<10} {description:<40} ${amount:>8.2f}  ${balance:>10.2f}\n"
        
        statement += f"""
----------------------------------------------------------------------------------

For questions about your account, please contact us at:
Phone: {bank['phone']}
Email: customer.service@{bank['website'].replace('www.', '')}

Thank you for banking with {bank['name']}!
"""
        
        return statement

    def _generate_ground_truth(self, text: str, customer: Dict, bank: Dict) -> Dict:
        """Generate ground truth annotations for PII in the statement."""
        entities = []
        
        # Find all instances of PII in the text
        self._add_entity(text, entities, customer['name'], "PERSON_NAME")
        self._add_entity(text, entities, customer['address'], "ADDRESS")
        self._add_entity(text, entities, customer['phone'], "PHONE_NUMBER")
        self._add_entity(text, entities, customer['email'], "EMAIL")
        self._add_entity(text, entities, customer['account_number'], "ACCOUNT_NUMBER")
        self._add_entity(text, entities, customer['routing_number'], "ROUTING_NUMBER")
        
        if "ssn" in customer:
            self._add_entity(text, entities, customer['ssn'], "SSN")
            
        if "credit_card" in customer:
            self._add_entity(text, entities, customer['credit_card'], "CREDIT_CARD_NUMBER")
            
        if "ip_address" in customer:
            self._add_entity(text, entities, customer['ip_address'], "IP_ADDRESS")
        
        self._add_entity(text, entities, bank['name'], "ORGANIZATION_NAME")
        self._add_entity(text, entities, bank['address'], "ADDRESS")
        self._add_entity(text, entities, bank['phone'], "PHONE_NUMBER")
        self._add_entity(text, entities, bank['website'], "WEBSITE")
        
        # Look for other people's names in transfer descriptions
        for line in text.split('\n'):
            if "TRANSFER" in line and "TO " in line:
                parts = line.split("TO ")
                if len(parts) > 1:
                    potential_name = parts[1].split("  ")[0]
                    if potential_name != "ACCOUNT" and potential_name not in customer['name']:
                        self._add_entity(text, entities, potential_name, "PERSON_NAME")
            elif "TRANSFER" in line and "FROM " in line:
                parts = line.split("FROM ")
                if len(parts) > 1:
                    potential_name = parts[1].split("  ")[0]
                    if potential_name != "ACCOUNT" and potential_name not in customer['name']:
                        self._add_entity(text, entities, potential_name, "PERSON_NAME")
        
        return {"entities": entities}

    def _add_entity(self, text: str, entities: List[Dict], entity_text: str, entity_type: str) -> None:
        """Add an entity to the ground truth if it exists in the text."""
        start = 0
        while True:
            start = text.find(entity_text, start)
            if start == -1:
                break
                
            entities.append({
                "type": entity_type,
                "text": entity_text,
                "start": start,
                "end": start + len(entity_text),
                "confidence": 1.0  # Ground truth has perfect confidence
            })
            
            start += len(entity_text)

    def _generate_pdf(self, 
                     customer: Dict, 
                     bank: Dict, 
                     start_date: datetime, 
                     end_date: datetime, 
                     transactions: List[Dict],
                     statement_format: Dict,
                     output_dir: Optional[str] = None) -> str:
        """Generate a PDF version of the bank statement."""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"statement_{bank['name'].replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create the PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Bank header
        elements.append(Paragraph(bank['name'], styles['Heading1']))
        elements.append(Paragraph(bank['address'], styles['Normal']))
        elements.append(Paragraph(f"Phone: {bank['phone']}", styles['Normal']))
        elements.append(Paragraph(f"Website: {bank['website']}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Statement header
        elements.append(Paragraph("ACCOUNT STATEMENT", styles['Heading2']))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            f"Statement Period: {start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}", 
            styles['Normal']
        ))
        elements.append(Spacer(1, 12))
        
        # Customer information
        elements.append(Paragraph("CUSTOMER INFORMATION:", styles['Heading3']))
        elements.append(Paragraph(customer['name'], styles['Normal']))
        elements.append(Paragraph(customer['address'], styles['Normal']))
        elements.append(Paragraph(f"Phone: {customer['phone']}", styles['Normal']))
        elements.append(Paragraph(f"Email: {customer['email']}", styles['Normal']))
        
        # Add SSN if present
        if "ssn" in customer:
            elements.append(Paragraph(f"SSN: {customer['ssn']}", styles['Normal']))
        
        # Add credit card if present
        if "credit_card" in customer:
            elements.append(Paragraph(f"Credit Card: {customer['credit_card']}", styles['Normal']))
            
        # Add IP address if present
        if "ip_address" in customer:
            elements.append(Paragraph(f"Last Login IP: {customer['ip_address']}", styles['Normal']))
            
        elements.append(Spacer(1, 12))
        
        # Account summary
        elements.append(Paragraph("ACCOUNT SUMMARY:", styles['Heading3']))
        elements.append(Paragraph(
            f"Account Number: XXXX-XXXX-XXXX-{customer['account_number'][-4:]}", 
            styles['Normal']
        ))
        elements.append(Paragraph(f"Routing Number: {customer['routing_number']}", styles['Normal']))
        elements.append(Paragraph(
            f"Beginning Balance: ${transactions[0]['balance'] - transactions[0]['amount']:.2f}", 
            styles['Normal']
        ))
        elements.append(Paragraph(f"Ending Balance: ${transactions[-1]['balance']:.2f}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Transaction history
        elements.append(Paragraph("TRANSACTION HISTORY:", styles['Heading3']))
        elements.append(Spacer(1, 6))
        
        # Create transaction table
        data = [["Date", "Description", "Amount", "Balance"]]
        for transaction in transactions:
            data.append([
                transaction['date'],
                transaction['description'],
                f"${transaction['amount']:.2f}",
                f"${transaction['balance']:.2f}"
            ])
            
        table = Table(data, colWidths=[80, 250, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Footer
        elements.append(Paragraph("For questions about your account, please contact us at:", styles['Normal']))
        elements.append(Paragraph(f"Phone: {bank['phone']}", styles['Normal']))
        elements.append(Paragraph(
            f"Email: customer.service@{bank['website'].replace('www.', '')}", 
            styles['Normal']
        ))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"Thank you for banking with {bank['name']}!", styles['Normal']))
        
        # Build the PDF
        doc.build(elements)
        
        return filepath

    def generate_dataset(self, 
                        num_samples: int = 10, 
                        output_dir: Optional[str] = None,
                        include_pdfs: bool = False) -> List[Dict]:
        """
        Generate a dataset of synthetic bank statements.

        Args:
            num_samples: Number of samples to generate (default: 10)
            output_dir: Directory to save the samples (default: None)
            include_pdfs: Whether to generate PDF versions of the statements (default: False)

        Returns:
            A list of dictionaries containing the generated samples
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
            
        os.makedirs(output_dir, exist_ok=True)
        
        samples = []
        
        for i in range(num_samples):
            # Randomly select format and distribution
            format_name = random.choice(self.statement_formats)
            pii_distribution_name = random.choice(self.pii_distributions)
            num_transactions = random.randint(10, 30)
            
            # Generate the sample
            statement_text, ground_truth, pdf_path = self.generate_statement(
                format_name=format_name,
                pii_distribution_name=pii_distribution_name,
                num_transactions=num_transactions,
                include_pdf=include_pdfs,
                output_dir=output_dir
            )
            
            # Save the statement text
            text_path = os.path.join(output_dir, f"statement_{i+1}.txt")
            with open(text_path, 'w') as f:
                f.write(statement_text)
            
            # Save the ground truth
            ground_truth_path = os.path.join(output_dir, f"statement_{i+1}_ground_truth.json")
            with open(ground_truth_path, 'w') as f:
                json.dump(ground_truth, f, indent=2)
            
            # Add to samples
            samples.append({
                "id": i+1,
                "format": format_name,
                "pii_distribution": pii_distribution_name,
                "num_transactions": num_transactions,
                "text_path": text_path,
                "ground_truth_path": ground_truth_path,
                "pdf_path": pdf_path,
                "entity_count": len(ground_truth["entities"]),
                "entity_types": {entity["type"] for entity in ground_truth["entities"]}
            })
            
            print(f"Generated sample {i+1}/{num_samples}")
            
        # Save dataset metadata
        metadata_path = os.path.join(output_dir, "dataset_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump({
                "num_samples": num_samples,
                "samples": samples,
                "generated_at": datetime.now().isoformat(),
            }, f, indent=2)
            
        return samples


def main():
    """Main function to generate synthetic bank statement samples."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic bank statement samples")
    parser.add_argument("--num-samples", type=int, default=10, help="Number of samples to generate")
    parser.add_argument("--output-dir", default=None, help="Output directory for samples")
    parser.add_argument("--include-pdfs", action="store_true", help="Generate PDF versions of the statements")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    generator = EnhancedBankStatementGenerator(seed=args.seed)
    samples = generator.generate_dataset(
        num_samples=args.num_samples,
        output_dir=args.output_dir,
        include_pdfs=args.include_pdfs
    )
    
    print(f"Generated {len(samples)} samples")


if __name__ == "__main__":
    main()