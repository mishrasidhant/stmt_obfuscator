#!/usr/bin/env python3
"""
Generate synthetic bank statement samples with ground truth annotations.

This script creates realistic bank statement text samples with PII and
generates corresponding ground truth annotations for evaluation.
"""

import argparse
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from faker import Faker


class BankStatementGenerator:
    """
    A class for generating synthetic bank statements with ground truth PII annotations.
    """

    def __init__(self, seed: int = None):
        """
        Initialize the BankStatementGenerator.

        Args:
            seed: Random seed for reproducibility (default: None)
        """
        if seed is not None:
            random.seed(seed)
            
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
            "Truist Bank"
        ]
        
        # Transaction descriptions for generating realistic statements
        self.transaction_types = [
            "PURCHASE", "PAYMENT", "DEPOSIT", "WITHDRAWAL", "TRANSFER", 
            "ATM WITHDRAWAL", "CHECK", "DIRECT DEPOSIT", "INTEREST", "FEE"
        ]
        
        self.merchants = [
            "AMAZON", "WALMART", "TARGET", "COSTCO", "KROGER", "STARBUCKS", 
            "UBER", "NETFLIX", "SPOTIFY", "APPLE", "GOOGLE", "MICROSOFT",
            "HOME DEPOT", "LOWES", "BEST BUY", "MCDONALDS", "CHIPOTLE",
            "SHELL", "EXXON", "CHEVRON", "DELTA", "AMERICAN AIRLINES",
            "HILTON", "MARRIOTT", "AIRBNB"
        ]

    def generate_statement(self) -> Tuple[str, Dict]:
        """
        Generate a synthetic bank statement with ground truth annotations.

        Returns:
            A tuple containing:
                - The generated bank statement text
                - A dictionary with ground truth PII annotations
        """
        # Generate customer information
        customer = {
            "name": self.faker.name(),
            "address": self.faker.address().replace('\n', ', '),
            "account_number": f"{random.randint(10000000, 99999999)}",
            "routing_number": f"{random.randint(100000000, 999999999)}",
            "phone": self.faker.phone_number(),
            "email": self.faker.email(),
            "ssn_last4": f"{random.randint(1000, 9999)}"
        }
        
        # Generate bank information
        bank = {
            "name": random.choice(self.bank_names),
            "address": self.faker.address().replace('\n', ', '),
            "phone": self.faker.phone_number(),
            "website": f"www.{self.faker.domain_name()}"
        }
        
        # Generate statement period
        end_date = datetime.now().replace(day=random.randint(1, 28))
        start_date = end_date - timedelta(days=30)
        
        # Generate transactions
        num_transactions = random.randint(10, 20)
        transactions = []
        
        balance = random.randint(1000, 10000)
        
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
                if random.random() < 0.5:
                    other_person = self.faker.name()
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
        
        # Generate the statement text
        statement_text = self._generate_statement_text(customer, bank, start_date, end_date, transactions)
        
        # Generate ground truth annotations
        ground_truth = self._generate_ground_truth(statement_text, customer, bank)
        
        return statement_text, ground_truth

    def _generate_statement_text(self, customer: Dict, bank: Dict, 
                                start_date: datetime, end_date: datetime, 
                                transactions: List[Dict]) -> str:
        """
        Generate the bank statement text.

        Args:
            customer: Customer information
            bank: Bank information
            start_date: Statement start date
            end_date: Statement end date
            transactions: List of transactions

        Returns:
            The generated bank statement text
        """
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

ACCOUNT SUMMARY:
Account Number: XXXX-XXXX-XXXX-{customer['account_number'][-4:]}
Routing Number: {customer['routing_number']}
Beginning Balance: ${transactions[0]['balance'] - transactions[0]['amount']:.2f}
Ending Balance: ${transactions[-1]['balance']:.2f}

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
        """
        Generate ground truth annotations for PII in the statement.

        Args:
            text: The generated statement text
            customer: Customer information
            bank: Bank information

        Returns:
            A dictionary with ground truth PII annotations
        """
        entities = []
        
        # Find all instances of PII in the text
        self._add_entity(text, entities, customer['name'], "PERSON_NAME")
        self._add_entity(text, entities, customer['address'], "ADDRESS")
        self._add_entity(text, entities, customer['phone'], "PHONE_NUMBER")
        self._add_entity(text, entities, customer['email'], "EMAIL")
        self._add_entity(text, entities, customer['account_number'], "ACCOUNT_NUMBER")
        self._add_entity(text, entities, customer['routing_number'], "ROUTING_NUMBER")
        
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
        """
        Add an entity to the ground truth if it exists in the text.

        Args:
            text: The full text to search in
            entities: The list of entities to append to
            entity_text: The entity text to search for
            entity_type: The type of the entity
        """
        start = 0
        while True:
            start = text.find(entity_text, start)
            if start == -1:
                break
                
            entities.append({
                "type": entity_type,
                "text": entity_text,
                "start": start,
                "end": start + len(entity_text)
            })
            
            start += len(entity_text)


def main():
    """
    Main function to generate synthetic bank statement samples.
    """
    parser = argparse.ArgumentParser(description="Generate synthetic bank statement samples")
    parser.add_argument("--num-samples", type=int, default=5, help="Number of samples to generate")
    parser.add_argument("--output-dir", default="../data", help="Output directory for samples")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    generator = BankStatementGenerator(seed=args.seed)
    
    for i in range(args.num_samples):
        statement_text, ground_truth = generator.generate_statement()
        
        # Save the statement text
        with open(os.path.join(args.output_dir, f"statement_{i+1}.txt"), 'w') as f:
            f.write(statement_text)
        
        # Save the ground truth
        with open(os.path.join(args.output_dir, f"statement_{i+1}_ground_truth.json"), 'w') as f:
            json.dump(ground_truth, f, indent=2)
        
        print(f"Generated sample {i+1}/{args.num_samples}")


if __name__ == "__main__":
    main()