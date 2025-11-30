import csv
import os
import json
from typing import List, Dict, Optional
from .modelle import Tool, User, Ruestwerkzeug
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, tools_csv_path: str, users_csv_path: str):
        self.tools_csv_path = tools_csv_path
        self.users_csv_path = users_csv_path
        self.toolbox_csv_path = os.path.join(os.path.dirname(tools_csv_path), "WKZKästen.csv")
        self.ruest_csv_path = os.path.join(os.path.dirname(tools_csv_path), "ruestwerkzeuge.csv")
        self.drawer_config_path = os.path.join(os.path.dirname(tools_csv_path), "drawer_config.json")
        
        self.fieldnames = [] # Store CSV headers for main file
        self.toolbox_fieldnames = [] # Store CSV headers for toolbox file
        self.ruest_fieldnames = ['ID', 'Name', 'Kasten', 'Lade', 'Fach', 'Bestand', 'MinBestand']
        
        # Caching
        self._tools_cache: Optional[List[Tool]] = None
        self._ruest_cache: Optional[List[Ruestwerkzeug]] = None
        self._users_cache: Optional[List[dict]] = None
        self._drawer_config_cache: Optional[Dict] = None

    # ... (existing methods)

    # --- Drawer Configuration Methods ---

    def load_drawer_config(self) -> Dict:
        if self._drawer_config_cache is not None:
            return self._drawer_config_cache
            
        if not os.path.exists(self.drawer_config_path):
            return {}
            
        try:
            with open(self.drawer_config_path, 'r', encoding='utf-8') as f:
                self._drawer_config_cache = json.load(f)
                return self._drawer_config_cache
        except Exception as e:
            logger.error(f"Error loading drawer config: {e}")
            return {}

    def save_drawer_config(self, config: Dict):
        self._drawer_config_cache = config
        try:
            with open(self.drawer_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving drawer config: {e}")
            raise

    def get_drawer_grid(self, kasten: int, lade: int) -> tuple[int, int]:
        """Returns (rows, cols) for the specified drawer. Defaults to (4, 6)."""
        config = self.load_drawer_config()
        k_str = str(kasten)
        l_str = str(lade)
        
        if k_str in config and l_str in config[k_str]:
            cfg = config[k_str][l_str]
            return cfg.get('rows', 4), cfg.get('cols', 6)
        
        return 4, 6 # Default


    def clear_cache(self):
        """Clear all data caches to force reload from disk."""
        self._tools_cache = None
        self._ruest_cache = None
        self._users_cache = None

    def load_tools(self, force_reload: bool = False) -> List[Tool]:
        if self._tools_cache is not None and not force_reload:
            return self._tools_cache

        tools = []
        if not os.path.exists(self.tools_csv_path):
            logger.warning(f"Tools file not found: {self.tools_csv_path}")
            return []
        
        try:
            # Load Toolbox Data first
            toolbox_data_map = {}
            if os.path.exists(self.toolbox_csv_path):
                try:
                    with open(self.toolbox_csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
                        line = f.readline()
                        f.seek(0)
                        delimiter = ';' if ';' in line else ','
                        reader = csv.DictReader(f, delimiter=delimiter)
                        self.toolbox_fieldnames = reader.fieldnames if reader.fieldnames else []
                        for row in reader:
                            name = row.get('Name', '').strip()
                            if name:
                                toolbox_data_map[name] = row
                except Exception as e:
                    logger.error(f"Error reading toolbox CSV: {e}")

            with open(self.tools_csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
                line = f.readline()
                f.seek(0)
                delimiter = ';' if ';' in line else ','
                
                reader = csv.DictReader(f, delimiter=delimiter)
                self.fieldnames = reader.fieldnames if reader.fieldnames else []
                
                for row in reader:
                    try:
                        raw_status = row.get('Status', '').strip()
                        status = raw_status
                        if raw_status.upper() == 'MASCHIENE':
                            status = 'maschine'
                        elif raw_status.upper() == 'GERÜSTET':
                            status = 'gerüstet'
                        elif raw_status.upper() in ['RÜSTWERKZEUG', 'RÜSTWERKZEUGE']:
                            status = 'Rüstwerkzeuge'
                        
                        # Extract known fields
                        t_id = row.get('WZ.Nr.', row.get('ID', '')).strip()
                        t_name = row.get('Name', '').strip()
                        t_lager = row.get('Pos.', row.get('Lagerplatz', '')).strip()
                        
                        # Merge with toolbox data
                        extra = {k: (v or '') for k, v in row.items() if k not in ['WZ.Nr.', 'ID', 'Name', 'Status', 'Pos.', 'Lagerplatz']}
                        
                        if t_name in toolbox_data_map:
                            # Add toolbox data to extra, excluding Name
                            tb_row = toolbox_data_map[t_name]
                            for k, v in tb_row.items():
                                if k != 'Name':
                                    extra[k] = v or ''

                        # Initialize per-toolbox status if not present
                        # This ensures we have independent status for each toolbox
                        herkunft = extra.get('Herkunft_Kasten')
                        if herkunft is None:
                            herkunft = ''
                        
                        # Normalize herkunft to just the number if possible, or keep string
                        herkunft_id = '0'
                        if 'Werkzeugkasten' in herkunft:
                            try:
                                herkunft_id = herkunft.split(' ')[-1]
                            except:
                                pass
                        
                        for i in range(1, 5):
                            key = f'Status_Box_{i}'
                            machine_key = f'Maschine_Box_{i}'
                            
                            if key not in extra or extra[key] == '':
                                # Initialize with main status if not present
                                # Special case: if there's a machine assignment for this box, set to 'maschine'
                                if machine_key in extra and extra[machine_key]:
                                    extra[key] = 'maschine'
                                else:
                                    # Use the main status as default
                                    extra[key] = status

                        tools.append(Tool(
                            id=t_id,
                            name=t_name,
                            status=status,
                            lagerplatz=t_lager,
                            extra_data=extra
                        ))
                    except Exception as e:
                        logger.error(f"Error parsing tool row: {e}")
                        continue
                        
            self._tools_cache = tools
            return tools
            
        except Exception as e:
            logger.error(f"Critical error loading tools: {e}")
            return []

    def delete_tool(self, tool_id: str) -> bool:
        tools = self.load_tools()
        initial_len = len(tools)
        tools = [t for t in tools if t.id != tool_id]
        
        if len(tools) < initial_len:
            self.save_tools(tools)
            return True
        return False

    def save_tools(self, tools: List[Tool]):
        # Update cache
        self._tools_cache = tools
        
        try:
            # Ensure we have fieldnames. If new file, define defaults.
            if not self.fieldnames:
                self.fieldnames = ['WZ.Nr.', 'Name', 'Status', 'Pos.']
                
            # Separate core and extra keys
            # Core keys are fixed based on what we know belongs in werkzeuge.csv
            # But we should respect self.fieldnames if loaded
            
            # We need to identify which keys belong to toolbox csv
            # If we loaded it, we have self.toolbox_fieldnames
            # If not, we might need to guess or define them.
            # Based on migration, we know the split.
            
            # Core columns from migration script:
            core_columns_set = {
                'WZ.Nr.', 'Name', 'Durchmesser', 'Schaft-D', 'Werkzeug-L', 'Schneiden-L', 
                'Oberer-D', 'Untere-L', 'Spannmittel', 'Halter-D', 'Gesamt-L', 
                'WZ-Hersteller', 'Sim.Farbe', 'Status', 'Pos.'
            }
            
            with open(self.tools_csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames, delimiter=';')
                writer.writeheader()
                
                for tool in tools:
                    row = {}
                    # Map Tool fields to CSV fields
                    row['WZ.Nr.'] = tool.id
                    row['Name'] = tool.name
                    row['Pos.'] = tool.lagerplatz
                    
                    # Restore status format
                    if tool.status == 'maschine':
                        row['Status'] = 'MASCHIENE'
                    elif tool.status == 'gerüstet':
                        row['Status'] = 'GERÜSTET'
                    elif tool.status == 'Rüstwerkzeuge':
                        row['Status'] = 'RÜSTWERKZEUG'
                    else:
                        row['Status'] = tool.status
                    
                    # Add other core fields from extra_data
                    for k, v in tool.extra_data.items():
                        if k in self.fieldnames and k not in ['WZ.Nr.', 'Name', 'Status', 'Pos.']:
                            row[k] = v
                    
                    # Ensure all fields exist
                    for f_name in self.fieldnames:
                        if f_name not in row:
                            row[f_name] = ''
                            
                    writer.writerow(row)

            # Save Toolbox Data
            if not self.toolbox_fieldnames:
                 # If we didn't load it, define defaults or infer
                 self.toolbox_fieldnames = ['Name', 'Herkunft_Kasten', 'Maschine', 
                                            'Status_Box_1', 'Status_Box_2', 'Status_Box_3', 'Status_Box_4',
                                            'Maschine_Box_1', 'Maschine_Box_2', 'Maschine_Box_3', 'Maschine_Box_4',
                                            'OriginalStatus_Box_1', 'OriginalStatus_Box_2', 'OriginalStatus_Box_3']

            # Collect all keys that are NOT in core fieldnames but are in extra_data
            all_extra_keys = set(self.toolbox_fieldnames)
            for t in tools:
                for k in t.extra_data.keys():
                    if k not in self.fieldnames and k != 'Name':
                        all_extra_keys.add(k)
            
            # Sort and update toolbox fieldnames
            final_toolbox_fieldnames = [f for f in self.toolbox_fieldnames if f in all_extra_keys]
            for k in sorted(all_extra_keys):
                if k not in final_toolbox_fieldnames:
                    final_toolbox_fieldnames.append(k)
            
            # Ensure Name is first
            if 'Name' in final_toolbox_fieldnames:
                final_toolbox_fieldnames.remove('Name')
            final_toolbox_fieldnames.insert(0, 'Name')

            with open(self.toolbox_csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=final_toolbox_fieldnames, delimiter=';')
                writer.writeheader()
                
                # Nur Werkzeuge mit Status != "Rüstwerkzeuge" in WKZKästen.csv speichern
                for tool in tools:
                    # Überspringe Rüstwerkzeuge - die gehören nur in ruestwerkzeuge.csv
                    if tool.status == 'Rüstwerkzeuge':
                        continue
                        
                    row = {'Name': tool.name}
                    for k, v in tool.extra_data.items():
                        if k in final_toolbox_fieldnames:
                            row[k] = v
                    
                    # Ensure all fields exist
                    for f_name in final_toolbox_fieldnames:
                        if f_name not in row:
                            row[f_name] = ''
                    writer.writerow(row)
        except Exception as e:
            logger.error(f"Error saving tools: {e}")
            raise

    def load_users(self) -> List[dict]:
        if self._users_cache is not None:
            return self._users_cache

        users = []
        if not os.path.exists(self.users_csv_path):
            return []
        
        try:
            with open(self.users_csv_path, mode='r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Strip whitespace and carriage returns from all values
                    cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
                    # Skip empty rows
                    if cleaned_row.get('Username'):
                        users.append(cleaned_row)
            self._users_cache = users
            return users
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return []
    
    def save_users(self, users: List[dict]):
         self._users_cache = users
         try:
             with open(self.users_csv_path, mode='w', newline='', encoding='utf-8') as f:
                fieldnames = ['Username', 'Password', 'Role']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for user in users:
                    writer.writerow(user)
         except Exception as e:
             logger.error(f"Error saving users: {e}")
             raise

    def add_user(self, username, password, role):
        users = self.load_users()
        if any(u['Username'] == username for u in users):
            return False # User exists
        
        hashed = self.hash_password(password)
        users.append({'Username': username, 'Password': hashed, 'Role': role})
        self.save_users(users)
        return True

    def delete_user(self, username):
        users = self.load_users()
        users = [u for u in users if u['Username'] != username]
        self.save_users(users)

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def get_toolbox_path(self, toolbox_id):
        dir_name = os.path.dirname(self.tools_csv_path)
        return os.path.join(dir_name, f"toolbox_{toolbox_id}.csv")

    def load_user_toolbox(self, toolbox_id) -> List[str]:
        """Returns a list of Tool IDs in the specified toolbox (1-4)"""
        path = self.get_toolbox_path(toolbox_id)
        if not os.path.exists(path):
            return []
        ids = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        ids.append(row[0])
        except Exception as e:
            logger.error(f"Error loading user toolbox {toolbox_id}: {e}")
        return ids

    def save_user_toolbox(self, toolbox_id, tool_ids: List[str]):
        path = self.get_toolbox_path(toolbox_id)
        try:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for tid in tool_ids:
                    writer.writerow([tid])
        except Exception as e:
            logger.error(f"Error saving user toolbox {toolbox_id}: {e}")

    # --- Rüstwerkzeug Methods ---

    def load_ruestwerkzeuge(self, force_reload: bool = False) -> List[Ruestwerkzeug]:
        if self._ruest_cache is not None and not force_reload:
            return self._ruest_cache

        tools = []
        if not os.path.exists(self.ruest_csv_path):
            return []
        
        try:
            with open(self.ruest_csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    try:
                        tools.append(Ruestwerkzeug(
                            id=row['ID'],
                            name=row['Name'],
                            kasten=int(row['Kasten']),
                            lade=int(row['Lade']),
                            fach=int(row['Fach']),
                            bestand=int(row['Bestand']),
                            min_bestand=int(row.get('MinBestand', 0))
                        ))
                    except (ValueError, KeyError):
                        continue
            self._ruest_cache = tools
            return tools
        except Exception as e:
            logger.error(f"Error loading ruestwerkzeuge: {e}")
            return []

    def save_ruestwerkzeuge(self, tools: List[Ruestwerkzeug]):
        self._ruest_cache = tools
        try:
            with open(self.ruest_csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.ruest_fieldnames, delimiter=';')
                writer.writeheader()
                for tool in tools:
                    writer.writerow({
                        'ID': tool.id,
                        'Name': tool.name,
                        'Kasten': tool.kasten,
                        'Lade': tool.lade,
                        'Fach': tool.fach,
                        'Bestand': tool.bestand,
                        'MinBestand': tool.min_bestand
                    })
        except Exception as e:
            logger.error(f"Error saving ruestwerkzeuge: {e}")
            raise

    def check_location_availability(self, kasten: int, lade: int, fach: int, ignore_id: str = None) -> bool:
        """Check if a specific location is already occupied by another tool."""
        tools = self.load_ruestwerkzeuge()
        for tool in tools:
            if tool.id == ignore_id:
                continue
            if tool.kasten == kasten and tool.lade == lade and tool.fach == fach:
                return False # Location occupied
        return True

    def add_ruestwerkzeug(self, tool: Ruestwerkzeug) -> bool:
        tools = self.load_ruestwerkzeuge()
        if any(t.id == tool.id for t in tools):
            return False # ID exists
            
        # Check location availability - aber nur wenn ein Lagerplatz zugewiesen wurde
        # K=0/L=0/F=0 bedeutet "noch nicht zugewiesen" und ist immer erlaubt
        if tool.kasten != 0 or tool.lade != 0 or tool.fach != 0:
            if not self.check_location_availability(tool.kasten, tool.lade, tool.fach):
                raise ValueError(f"Lagerplatz K{tool.kasten}/L{tool.lade}/F{tool.fach} ist bereits belegt!")
            
        tools.append(tool)
        self.save_ruestwerkzeuge(tools)
        return True

    def update_ruestwerkzeug(self, tool: Ruestwerkzeug) -> bool:
        tools = self.load_ruestwerkzeuge()
        
        # Check location availability (ignoring self) - aber nur wenn ein Lagerplatz zugewiesen wurde
        # K=0/L=0/F=0 bedeutet "noch nicht zugewiesen" und ist immer erlaubt
        if tool.kasten != 0 or tool.lade != 0 or tool.fach != 0:
            if not self.check_location_availability(tool.kasten, tool.lade, tool.fach, ignore_id=tool.id):
                raise ValueError(f"Lagerplatz K{tool.kasten}/L{tool.lade}/F{tool.fach} ist bereits belegt!")

        for i, t in enumerate(tools):
            if t.id == tool.id:
                tools[i] = tool
                self.save_ruestwerkzeuge(tools)
                return True
        return False

    def delete_ruestwerkzeug(self, tool_id: str) -> bool:
        tools = self.load_ruestwerkzeuge()
        initial_len = len(tools)
        tools = [t for t in tools if t.id != tool_id]
        if len(tools) < initial_len:
            self.save_ruestwerkzeuge(tools)
            return True
        return False

