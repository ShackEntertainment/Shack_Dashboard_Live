def get_google_credentials():
    """Get Google Sheets credentials from Streamlit secrets or local file"""
    
    # Try Streamlit secrets - check both formats
    if hasattr(st, 'secrets'):
        try:
            # First try [google_sheets] format with JSON blob
            if 'google_sheets' in st.secrets:
                secrets = st.secrets['google_sheets']
                
                # Check if it's a JSON blob format
                if 'credentials' in secrets:
                    import json
                    creds_json = secrets['credentials']
                    if isinstance(creds_json, str):
                        creds_dict = json.loads(creds_json)
                    else:
                        creds_dict = creds_json
                else:
                    # It's flat format
                    private_key = secrets.get('private_key', '')
                    if '\\n' in private_key:
                        private_key = private_key.replace('\\n', '\n')
                    
                    creds_dict = {
                        "type": "service_account",
                        "project_id": secrets.get('project_id', ''),
                        "private_key_id": secrets.get('private_key_id', ''),
                        "private_key": private_key,
                        "client_email": secrets.get('client_email', ''),
                        "client_id": secrets.get('client_id', ''),
                        "auth_uri": secrets.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
                        "token_uri": secrets.get('token_uri', 'https://oauth2.googleapis.com/token'),
                        "auth_provider_x509_cert_url": secrets.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs'),
                        "client_x509_cert_url": secrets.get('client_x509_cert_url', ''),
                        "universe_domain": secrets.get('universe_domain', 'googleapis.com')
                    }
                
                return Credentials.from_service_account_info(creds_dict)
            
            # Fallback to [connections.gsheets] format
            elif 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
                secrets = st.secrets['connections']['gsheets']
                private_key = secrets.get('private_key', '')
                if '\\n' in private_key:
                    private_key = private_key.replace('\\n', '\n')
                
                creds_dict = {
                    "type": "service_account",
                    "project_id": secrets.get('project_id', ''),
                    "private_key_id": secrets.get('private_key_id', ''),
                    "private_key": private_key,
                    "client_email": secrets.get('client_email', ''),
                    "client_id": secrets.get('client_id', ''),
                    "auth_uri": secrets.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
                    "token_uri": secrets.get('token_uri', 'https://oauth2.googleapis.com/token'),
                    "auth_provider_x509_cert_url": secrets.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs'),
                    "client_x509_cert_url": secrets.get('client_x509_cert_url', ''),
                    "universe_domain": secrets.get('universe_domain', 'googleapis.com')
                }
                
                return Credentials.from_service_account_info(creds_dict)
                
        except Exception as e:
            st.error(f"Error loading credentials from secrets: {e}")
            return None
    
    # Fallback to local file
    if os.path.exists('shack_credentials.json'):
        try:
            return Credentials.from_service_account_file('shack_credentials.json')
        except Exception as e:
            st.error(f"Error loading local credentials: {e}")
            return None
    
    return None