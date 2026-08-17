import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Import credentials logic from existing data_sync to avoid duplication
try:
    from data_sync import get_google_credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    def get_google_credentials():
        return None

try:
    import gspread
except ImportError:
    pass

def load_news_data():
    """Load data from Shack_News_Network_Master"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
               pd.DataFrame(), pd.DataFrame(), {}, 
               "Google Sheets libraries not installed")
    
    try:
        creds = get_google_credentials()
        if not creds:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   "Failed to load credentials. Check Streamlit secrets.")
        
        gc = gspread.authorize(creds)
        
        try:
            # Open the News Network Spreadsheet
            spreadsheet = gc.open("Shack_News_Network_Master")
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   f"Cannot find 'Shack_News_Network_Master': {str(e)}")
        
        try:
            # Define worksheet names
            sheets = {
                'content': spreadsheet.worksheet("01_Content_Library"),
                'youtube': spreadsheet.worksheet("02_Youtube_Analytics"),
                'social': spreadsheet.worksheet("03_Social_Media_Metrics"),
                'referral': spreadsheet.worksheet("04_Referral_Monetization"),
                'campaign': spreadsheet.worksheet("05_Campaign_Tracking"),
                'snapshot': spreadsheet.worksheet("06_Snapshot")
            }
            
            # Read data
            content_df = pd.DataFrame(sheets['content'].get_all_records())
            youtube_df = pd.DataFrame(sheets['youtube'].get_all_records())
            social_df = pd.DataFrame(sheets['social'].get_all_records())
            referral_df = pd.DataFrame(sheets['referral'].get_all_records())
            campaign_df = pd.DataFrame(sheets['campaign'].get_all_records())
            
            # Read snapshot (single row summary)
            snapshot_data = sheets['snapshot'].get_all_values()
            snapshot_dict = {}
            if len(snapshot_data) > 1:
                headers = snapshot_data[0]
                values = snapshot_data[1]
                snapshot_dict = dict(zip(headers, values))
            
            return content_df, youtube_df, social_df, referral_df, campaign_df, snapshot_dict, None
            
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   f"Error reading worksheets: {str(e)}")
            
    except Exception as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
               pd.DataFrame(), pd.DataFrame(), {}, 
               f"Error: {str(e)}")