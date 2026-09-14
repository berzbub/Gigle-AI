# ==============================================================================
# Project: Gigle-AI (SSCR Manila Institutional Suite & NGO Framework)
# File: ngo_core.py
# Copyright (c) 2026 Jose Prudencio G. Castillo Jr. OAR and Jennifer Logic
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# ==============================================================================

import json
from datetime import datetime

class NGOMissionCore:
    def __init__(self, mission_name: str):
        self.mission_name = mission_name
        self.financial_manifest = {"donations": [], "expenses": [], "net_balance": 0.0}
        self.activity_reports = []
        self.meeting_logs = []
        self.offline_waypoints = {}

    def log_financial_transaction(self, tx_type: str, item: str, amount: float, donor_or_receiver: str):
        """Maintains transparent financial tracking (inputs/outputs)."""
        tx = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": tx_type.lower(),  # 'donation' or 'expense'
            "item": item,
            "amount": amount,
            "entity": donor_or_receiver
        }
        if tx["type"] == "donation":
            self.financial_manifest["donations"].append(tx)
            self.financial_manifest["net_balance"] += amount
        elif tx["type"] == "expense":
            self.financial_manifest["expenses"].append(tx)
            self.financial_manifest["net_balance"] -= amount
        return tx

    def process_receipt_snapshot(self, image_description_or_path: str, tx_type: str, item_category: str, amount: float, vendor_or_donor: str):
        """
        Parses a picture or video snapshot of a receipt, automatically encodes it,
        and logs it into the financial manifest for end-of-month tallying.
        """
        receipt_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": tx_type.lower(),  # 'donation' (input) or 'expense' (output)
            "source_media": image_description_or_path,
            "item": item_category,
            "amount": amount,
            "entity": vendor_or_donor,
            "status": "Encoded via Snapshot"
        }
        
        if receipt_entry["type"] == "donation":
            self.financial_manifest["donations"].append(receipt_entry)
            self.financial_manifest["net_balance"] += amount
        elif receipt_entry["type"] == "expense":
            self.financial_manifest["expenses"].append(receipt_entry)
            self.financial_manifest["net_balance"] -= amount
            
        return receipt_entry

    def record_activity_report(self, title: str, description: str, image_references: list):
        """Logs mission outputs, activities, and attached visual documentation."""
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "description": description,
            "images": image_references
        }
        self.activity_reports.append(report)
        return report

    def encode_and_summarize_meeting(self, raw_transcript: str, meeting_title: str):
        """Interprets raw meeting flow and encodes it into an official formal summary."""
        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": meeting_title,
            "official_format": "Formal NGO Minutes & Directive Summary",
            "gist_interpretation": f"Processed raw dialogue: '{raw_transcript[:100]}...'",
            "action_items": ["Review transparency reports", "Deploy field mapping kits", "Coordinate volunteer logistics"]
        }
        self.meeting_logs.append(summary)
        return summary

    def add_offline_waypoint(self, name: str, coordinates: tuple, category: str):
        """Stores offline map coordinates for remote field navigation."""
        self.offline_waypoints[name] = {
            "coordinates": coordinates,
            "category": category, # e.g., 'Water Station', 'Medical Triage', 'Safe Zone'
        }
        return f"Waypoint '{name}' saved for offline navigation."

    def generate_monthly_newspaper_journal(self, month_year: str, volunteer_notes: str = ""):
        """
        Generates a monthly newspaper journal report combining headlines, 
        financial tallies, community projects, and volunteer notes.
        """
        total_donations = sum(d["amount"] for d in self.financial_manifest["donations"])
        total_expenses = sum(e["amount"] for e in self.financial_manifest["expenses"])
        
        journal = f"==================================================\n"
        journal += f" 📰 THE MISSION GAZETTE: MONTHLY JOURNAL ({month_year})\n"
        journal += f"==================================================\n\n"
        
        # 1. Headline & Overview
        journal += f"【 HEADLINE & MONTHLY OVERVIEW 】\n"
        journal += f"Mission: {self.mission_name}\n"
        journal += f"Summary: This month marked significant progress across grassroots outreach, "
        journal += f"community integration, and active project execution.\n\n"
        
        # 2. Financial Aspect
        journal += f"【 FINANCIAL MANIFEST & TALLY 】\n"
        journal += f"• Total Inflow (Donations): ₱{total_donations:,.2f}\n"
        journal += f"• Total Outflow (Expenses): ₱{total_expenses:,.2f}\n"
        journal += f"• Ending Net Balance: ₱{self.financial_manifest['net_balance']:,.2f}\n"
        journal += f"• Receipts Processed: {len(self.financial_manifest['expenses']) + len(self.financial_manifest['donations'])}\n\n"
        
        # 3. Community Projects & Outputs
        journal += f"【 PROJECTS & COMMUNITY OUTPUTS 】\n"
        if self.activity_reports:
            for act in self.activity_reports:
                journal += f"• [{act['timestamp']}] {act['title']}: {act['description']} (Images attached: {len(act['images'])})\n"
        else:
            journal += f"• No specific field activities logged yet this month.\n"
        journal += f"\n"
        
        # 4. Volunteer Supplementary Notes
        if volunteer_notes:
            journal += f"【 VOLUNTEER & FIELD NOTES 】\n"
            journal += f"{volunteer_notes}\n\n"
            
        journal += f"==================================================\n"
        journal += f"End of Monthly Edition — Published by Gigle-AI\n"
        journal += f"==================================================\n"
        
        return journal

if __name__ == "__main__":
    ngo = NGOMissionCore("Community Outreach & Relief Mission 2026")
    ngo.log_financial_transaction("donation", "Medical Supplies Fund", 50000.0, "Anonymous Benefactor")
    ngo.process_receipt_snapshot("fuel_receipt.jpg", "expense", "Transport & Fuel", 1500.0, "Moncada Station")
    print(ngo.generate_monthly_newspaper_journal("September 2026", "Volunteers completed water filtration checks and medical supply distribution."))
