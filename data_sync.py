def get_google_credentials():
    """Get Google Sheets credentials from Streamlit secrets or local file"""
    
    if hasattr(st, 'secrets'):
        try:
            # Try [google_sheets] format
            if 'google_sheets' in st.secrets:
                st.write("✅ Found [google_sheets] in secrets")  # Debug
                secrets = st.secrets['google_sheets']
                
                # Check if it's a JSON blob format
                if 'credentials' in secrets:
                    st.write("✅ Found 'credentials' key - parsing JSON blob")  # Debug
                    import json
                    creds_json = secrets['credentials']
                    st.write(f"Credentials type: {type(creds_json)}")  # Debug
                    
                    if isinstance(creds_json, str):
                        try:
                            creds_dict = json.loads(creds_json)
                            st.write("✅ JSON parsed successfully")  # Debug
                        except json.JSONDecodeError as je:
                            st.error(f"❌ JSON parse error: {je}")
                            return None
                    else:
                        creds_dict = creds_json
                    
                    # Try to create credentials
                    try:
                        creds = Credentials.from_service_account_info(creds_dict)
                        st.write("✅ Credentials created successfully!")  # Debug
                        return creds
                    except Exception as ce:
                        st.error(f"❌ Error creating credentials: {ce}")
                        st.error(f"Private key starts with: {creds_dict.get('private_key', '')[:50]}...")
                        return None
                        
                else:
                    st.write("Using flat format")  # Debug
                    # Flat format
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
                    
                    try:
                        creds = Credentials.from_service_account_info(creds_dict)
                        return creds
                    except Exception as ce:
                        st.error(f"❌ Error in flat format: {ce}")
                        return None
            
            # Try [connections.gsheets] format
            elif 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
                st.write("Found [connections.gsheets] format")
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
            else:
                st.write("❌ No credentials found in secrets")
                st.write(f"Available secrets keys: {list(st.secrets.keys())}")
                return None
                
        except Exception as e:
            st.error(f"❌ Unexpected error in get_google_credentials: {type(e).__name__}: {e}")
            import traceback
            st.error(traceback.format_exc())
            return None
    
    # Fallback to local file
    if os.path.exists('shack_credentials.json'):
        try:
            return Credentials.from_service_account_file('shack_credentials.json')
        except Exception as e:
            st.error(f"Error loading local credentials: {e}")
            return None
    
    return None