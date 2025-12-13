import pandas as pd
import numpy as np
import os
import re
import yaml
from typing import List, Dict, Tuple, Any
import json
from pathlib import Path
import ast

class MedicalDataProcessor:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.datasets_dir = self.base_dir / "datasets"
        self.models_dir = self.base_dir / "models"
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Medical knowledge base
        self.medical_knowledge = self.create_medical_knowledge_base()
    
    def create_medical_knowledge_base(self):
        """Create comprehensive medical knowledge base"""
        return {
            'symptoms': {
                'fever': {
                    'description': 'Elevated body temperature above normal (98.6°F/37°C)',
                    'possible_causes': ['Infection', 'Inflammation', 'Autoimmune disorders', 'Medication reaction'],
                    'first_aid': ['Rest', 'Hydration', 'Cool compresses', 'Over-the-counter fever reducers'],
                    'when_to_see_doctor': 'If fever is above 104°F (40°C), lasts more than 3 days, or is accompanied by severe symptoms'
                },
                'headache': {
                    'description': 'Pain in head or neck region',
                    'types': ['Tension', 'Migraine', 'Cluster', 'Sinus'],
                    'relief': ['Rest in dark room', 'Hydration', 'Over-the-counter pain relief', 'Avoid triggers'],
                    'emergency_signs': 'Sudden severe headache, headache after injury, with fever/stiff neck/confusion'
                },
                'cough': {
                    'description': 'Reflex to clear throat and airways',
                    'types': ['Dry', 'Productive', 'Acute', 'Chronic'],
                    'remedies': ['Hydration', 'Honey', 'Steam inhalation', 'Humidifier'],
                    'warning_signs': 'Coughing blood, difficulty breathing, chest pain, lasting more than 3 weeks'
                },
                'rash': {
                    'description': 'Change in skin color or texture',
                    'possible_causes': ['Allergies', 'Infections', 'Autoimmune conditions', 'Medications'],
                    'first_aid': ['Avoid scratching', 'Cool compresses', 'Over-the-counter antihistamines'],
                    'when_to_see_doctor': 'If rash is widespread, painful, or accompanied by fever or difficulty breathing'
                },
                'pain': {
                    'description': 'Unpleasant sensory experience',
                    'types': ['Acute', 'Chronic', 'Localized', 'Radiating'],
                    'management': ['Rest', 'Over-the-counter pain relief', 'Heat/cold therapy'],
                    'emergency_signs': 'Severe pain, chest pain, abdominal pain, pain after injury'
                },
                'fatigue': {
                    'description': 'Extreme tiredness and lack of energy',
                    'possible_causes': ['Anemia', 'Thyroid issues', 'Sleep disorders', 'Chronic conditions'],
                    'management': ['Adequate sleep', 'Balanced diet', 'Regular exercise', 'Stress reduction'],
                    'when_to_see_doctor': 'If persistent, severe, or accompanied by other symptoms'
                }
            },
            'vaccinations': {
                'covid_19': {
                    'types': ['mRNA (Pfizer, Moderna)', 'Vector (Johnson & Johnson)', 'Protein subunit'],
                    'schedule': 'Primary series + boosters as recommended',
                    'side_effects': ['Pain at injection site', 'Fatigue', 'Headache', 'Fever'],
                    'effectiveness': 'High effectiveness against severe disease'
                },
                'influenza': {
                    'recommendation': 'Annual vaccination for everyone 6 months and older',
                    'types': ['Standard dose', 'High dose (for seniors)', 'Egg-free'],
                    'best_time': 'Fall, before flu season peaks'
                },
                'hepatitis_b': {
                    'schedule': '3-dose series (0, 1, and 6 months)',
                    'recommended_for': ['Infants', 'Healthcare workers', 'People with chronic liver disease'],
                    'effectiveness': 'Over 95% effective'
                }
            },
            'diet_plans': {
                'diabetes': {
                    'focus': 'Blood sugar control',
                    'foods_to_eat': ['Non-starchy vegetables', 'Lean proteins', 'Whole grains', 'Healthy fats'],
                    'foods_to_limit': ['Sugary drinks', 'Refined carbs', 'Processed foods'],
                    'meal_timing': 'Regular meals and snacks throughout day'
                },
                'heart_health': {
                    'focus': 'Low cholesterol, low sodium',
                    'foods_to_eat': ['Fruits and vegetables', 'Whole grains', 'Fish', 'Nuts'],
                    'foods_to_avoid': ['Trans fats', 'High sodium foods', 'Red meat'],
                    'lifestyle': 'Combine with regular exercise'
                },
                'weight_management': {
                    'principle': 'Calorie balance',
                    'recommendations': ['Portion control', 'High fiber foods', 'Lean proteins', 'Regular meals'],
                    'tips': ['Stay hydrated', 'Mindful eating', 'Regular physical activity']
                },
                'celiac_disease': {
                    'focus': 'Gluten-free diet',
                    'foods_to_eat': ['Naturally gluten-free grains (rice, quinoa)', 'Fresh fruits and vegetables', 'Lean meats'],
                    'foods_to_avoid': ['Wheat, barley, rye', 'Processed foods with gluten', 'Beer and malt beverages'],
                    'important': 'Read labels carefully and avoid cross-contamination'
                }
            },
            'disease_prevention': {
                'general': [
                    'Regular hand washing',
                    'Balanced diet rich in fruits and vegetables',
                    'Regular physical activity (30 minutes daily)',
                    'Adequate sleep (7-9 hours per night)',
                    'Stress management techniques',
                    'Regular health check-ups and screenings',
                    'Avoid smoking and limit alcohol',
                    'Maintain healthy weight'
                ],
                'specific': {
                    'diabetes': 'Maintain healthy weight, exercise regularly, balanced diet with controlled carbohydrates',
                    'heart_disease': 'No smoking, control blood pressure and cholesterol, healthy diet, regular exercise',
                    'cancer': 'No tobacco, sun protection, healthy diet rich in antioxidants, regular screening',
                    'infections': 'Vaccinations, good hygiene, safe food handling, avoid close contact with sick individuals'
                }
            }
        }
    
    def load_all_datasets(self):
        """Load all medical datasets"""
        print("📊 Loading medical datasets...")
        
        datasets = {}
        
        try:
            # Load train_data_chatbot.csv
            df_chatbot = pd.read_csv(self.datasets_dir / "train_data_chatbot.csv")
            print(f"✅ Loaded train_data_chatbot.csv: {df_chatbot.shape}")
            datasets['chatbot'] = df_chatbot
        except Exception as e:
            print(f"❌ Error loading train_data_chatbot.csv: {e}")
            
        try:
            # Load medical_conversations.csv
            df_conv = pd.read_csv(self.datasets_dir / "medical_conversations.csv")
            print(f"✅ Loaded medical_conversations.csv: {df_conv.shape}")
            datasets['conversations'] = df_conv
        except Exception as e:
            print(f"❌ Error loading medical_conversations.csv: {e}")
            
        try:
            # Load train.csv
            df_train = pd.read_csv(self.datasets_dir / "train.csv")
            print(f"✅ Loaded train.csv: {df_train.shape}")
            datasets['train'] = df_train
        except Exception as e:
            print(f"❌ Error loading train.csv: {e}")
            
        try:
            # Load test.csv
            df_test = pd.read_csv(self.datasets_dir / "test.csv")
            print(f"✅ Loaded test.csv: {df_test.shape}")
            datasets['test'] = df_test
        except Exception as e:
            print(f"❌ Error loading test.csv: {e}")
            
        return datasets
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if pd.isna(text):
            return ""
        
        text = str(text)
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.lower().strip()
        
        return text
    
    def safe_eval_tags(self, tags_str):
        """Safely evaluate tags string"""
        if pd.isna(tags_str) or tags_str == "['']":
            return []
        try:
            # Handle both string representation of list and actual list
            if isinstance(tags_str, str):
                return ast.literal_eval(tags_str)
            elif isinstance(tags_str, list):
                return tags_str
            else:
                return []
        except:
            return []
    
    def extract_medical_entities(self, text):
        """Extract medical entities from text"""
        entities = []
        text_lower = text.lower()
        
        # Medical symptoms
        symptom_patterns = {
            'fever': r'\bfever\b|\btemperature\b|\bhot\b|\bchills\b',
            'headache': r'\bheadache\b|\bmigraine\b|\bhead pain\b',
            'cough': r'\bcough\b|\bcoughing\b',
            'pain': r'\bpain\b|\bhurt\b|\bsore\b|\bache\b',
            'rash': r'\brash\b|\bitching\b|\bitchy\b',
            'fatigue': r'\bfatigue\b|\btired\b|\bexhausted\b|\bweak\b',
            'nausea': r'\bnausea\b|\bvomit\b|\bthrow up\b|\bsick to stomach\b',
            'dizziness': r'\bdizziness\b|\bdizzy\b|\bvertigo\b',
            'swelling': r'\bswelling\b|\bswollen\b|\binflammation\b',
            'infection': r'\binfection\b|\binfected\b'
        }
        
        # Body parts
        body_parts = {
            'head': r'\bhead\b',
            'chest': r'\bchest\b',
            'stomach': r'\bstomach\b|\babdomen\b|\bbelly\b',
            'back': r'\bback\b',
            'throat': r'\bthroat\b',
            'arm': r'\barm\b',
            'leg': r'\bleg\b',
            'shoulder': r'\bshoulder\b',
            'neck': r'\bneck\b',
            'knee': r'\bknee\b'
        }
        
        # Diseases/conditions
        diseases = {
            'diabetes': r'\bdiabet\b',
            'cancer': r'\bcancer\b',
            'hepatitis': r'\bhepatitis\b',
            'pneumonia': r'\bpneumonia\b',
            'allergy': r'\ballerg\b',
            'asthma': r'\basthma\b',
            'arthritis': r'\barthrit\b',
            'hypertension': r'\bhypertension\b|\bhigh blood pressure\b',
            'celiac': r'\bceliac\b',
            'stroke': r'\bstroke\b',
            'kidney': r'\bkidney\b',
            'liver': r'\bliver\b'
        }
        
        # Medications/Treatments
        treatments = {
            'antibiotic': r'\bantibiotic\b',
            'vaccine': r'\bvaccine\b|\bvaccination\b|\bshot\b',
            'medication': r'\bmedication\b|\bmedicine\b|\bdrug\b',
            'surgery': r'\bsurgery\b|\boperation\b'
        }
        
        # Extract entities
        for entity_type, pattern in symptom_patterns.items():
            if re.search(pattern, text_lower):
                entities.append({'entity': 'symptom', 'value': entity_type})
                
        for body_part, pattern in body_parts.items():
            if re.search(pattern, text_lower):
                entities.append({'entity': 'body_part', 'value': body_part})
                
        for disease, pattern in diseases.items():
            if re.search(pattern, text_lower):
                entities.append({'entity': 'disease', 'value': disease})
                
        for treatment, pattern in treatments.items():
            if re.search(pattern, text_lower):
                entities.append({'entity': 'treatment', 'value': treatment})
        
        return entities
    
    def process_chatbot_data(self, df):
        """Process train_data_chatbot.csv - Updated for your specific format"""
        intents = []
        
        for idx, row in df.iterrows():
            if pd.isna(row['short_question']) or pd.isna(row['short_answer']):
                continue
                
            question = self.clean_text(row['short_question'])
            answer = self.clean_text(row['short_answer'])
            
            if len(question) < 3 or len(answer) < 3:
                continue
            
            # Create intent based on tags or content
            tags = self.safe_eval_tags(row['tags'])
            if tags:
                intent_name = f"ask_{tags[0].replace(' ', '_').lower()}"
            else:
                # Create intent name from question content
                words = question.split()[:4]
                intent_name = f"medical_{'_'.join(words)}".replace('?', '').replace("'", "").replace('"', '')[:50]
                intent_name = re.sub(r'[^a-zA-Z0-9_]', '', intent_name)
            
            entities = self.extract_medical_entities(question)
            
            intent_data = {
                'intent': intent_name,
                'examples': [question],
                'responses': [answer],
                'entities': entities,
                'source': 'chatbot_data'
            }
            intents.append(intent_data)
            
        return intents
    
    def process_conversations_data(self, df):
        """Process medical_conversations.csv - Updated for your format"""
        intents = []
        
        for idx, row in df.iterrows():
            if pd.isna(row['conversations']):
                continue
                
            conversation = row['conversations']
            disease = row['disease'] if 'disease' in df.columns and pd.notna(row['disease']) else 'general'
            
            # Split conversation into user and bot messages
            messages = conversation.split('</s>')
            user_messages = []
            bot_messages = []
            
            for msg in messages:
                if 'User:' in msg:
                    user_msg = msg.replace('User:', '').strip()
                    if user_msg:
                        user_messages.append(user_msg)
                elif 'Bot:' in msg:
                    bot_msg = msg.replace('Bot:', '').strip()
                    if bot_msg:
                        bot_messages.append(bot_msg)
            
            # Pair user messages with bot responses
            for i, (user_msg, bot_msg) in enumerate(zip(user_messages, bot_messages)):
                if len(user_msg) > 5 and len(bot_msg) > 5:
                    user_clean = self.clean_text(user_msg)
                    bot_clean = self.clean_text(bot_msg)
                    
                    # Create meaningful intent name
                    intent_name = f"conversation_{disease}_{idx}_{i}"
                    entities = self.extract_medical_entities(user_clean)
                    
                    intent_data = {
                        'intent': intent_name,
                        'examples': [user_clean],
                        'responses': [bot_clean],
                        'entities': entities,
                        'source': 'conversations_data'
                    }
                    intents.append(intent_data)
                    
        return intents
    
    def extract_conversation_pairs(self, conversation_text):
        """Extract human-AI conversation pairs from the formatted text"""
        pairs = []
        
        # Pattern to match [|Human|] and [|AI|] messages
        human_pattern = r'\[\|Human\|\]\s*(.*?)(?=\[\|AI\|\]|$)'
        ai_pattern = r'\[\|AI\|\]\s*(.*?)(?=\[\|Human\|\]|$)'
        
        human_messages = re.findall(human_pattern, conversation_text, re.DOTALL)
        ai_messages = re.findall(ai_pattern, conversation_text, re.DOTALL)
        
        # Pair human messages with AI responses
        for human_msg, ai_msg in zip(human_messages, ai_messages):
            human_clean = human_msg.strip()
            ai_clean = ai_msg.strip()
            
            if human_clean and ai_clean and len(human_clean) > 10 and len(ai_clean) > 10:
                pairs.append((human_clean, ai_clean))
        
        return pairs
    
    def process_train_test_data(self, df, dataset_name):
        """Process train.csv and test.csv - Updated for your format"""
        intents = []
        
        for idx, row in df.iterrows():
            if pd.isna(row['Conversation']):
                continue
                
            conversation = row['Conversation']
            
            # Extract conversation pairs
            pairs = self.extract_conversation_pairs(conversation)
            
            for i, (human_msg, ai_msg) in enumerate(pairs):
                human_clean = self.clean_text(human_msg)
                ai_clean = self.clean_text(ai_msg)
                
                if len(human_clean) > 10 and len(ai_clean) > 10:
                    # Create intent name
                    words = human_clean.split()[:4]
                    intent_name = f"{dataset_name}_{'_'.join(words)}".replace('?', '').replace("'", "").replace('"', '')[:50]
                    intent_name = re.sub(r'[^a-zA-Z0-9_]', '', intent_name)
                    
                    entities = self.extract_medical_entities(human_clean)
                    
                    intent_data = {
                        'intent': intent_name,
                        'examples': [human_clean],
                        'responses': [ai_clean],
                        'entities': entities,
                        'source': f'{dataset_name}_data'
                    }
                    intents.append(intent_data)
                    
        return intents
    
    def create_specialized_medical_intents(self):
        """Create specialized medical intents based on knowledge base"""
        medical_intents = []
        
        # Vaccine information intents
        vaccine_examples = [
            "tell me about covid vaccine",
            "what vaccines do i need",
            "information about hepatitis b vaccination",
            "flu shot schedule",
            "vaccine side effects",
            "are vaccines safe",
            "when to get vaccinated",
            "covid booster information",
            "influenza vaccine details"
        ]
        
        medical_intents.append({
            'intent': 'ask_vaccine_info',
            'examples': vaccine_examples,
            'responses': ["I can provide information about various vaccines including COVID-19, influenza, hepatitis B, and more. Which specific vaccine are you interested in?"],
            'entities': [],
            'source': 'knowledge_base'
        })
        
        # Symptom checker intents
        symptom_examples = [
            "i have fever and headache",
            "check my symptoms",
            "what does this symptom mean",
            "i feel dizzy and nauseous",
            "symptom checker",
            "do i need to see a doctor for these symptoms",
            "rash and itching what to do",
            "persistent cough advice"
        ]
        
        medical_intents.append({
            'intent': 'symptom_check',
            'examples': symptom_examples,
            'responses': ["I can help you understand common symptoms. Please describe what you're experiencing in detail, including duration and severity."],
            'entities': [],
            'source': 'knowledge_base'
        })
        
        # Diet and nutrition intents
        diet_examples = [
            "diet for diabetes",
            "healthy eating plan",
            "nutrition advice",
            "what to eat for heart health",
            "weight management diet",
            "balanced diet plan",
            "gluten free diet for celiac",
            "foods to lower cholesterol"
        ]
        
        medical_intents.append({
            'intent': 'ask_diet_advice',
            'examples': diet_examples,
            'responses': ["I can provide general dietary recommendations for various health conditions. What specific dietary information are you looking for?"],
            'entities': [],
            'source': 'knowledge_base'
        })
        
        # Disease prevention intents
        prevention_examples = [
            "how to prevent heart disease",
            "cancer prevention tips",
            "ways to stay healthy",
            "disease prevention methods",
            "how to avoid getting sick",
            "prevention of diabetes",
            "healthy lifestyle tips",
            "wellness practices"
        ]
        
        medical_intents.append({
            'intent': 'ask_prevention',
            'examples': prevention_examples,
            'responses': ["I can share information about disease prevention and healthy lifestyle practices. What specific prevention information are you interested in?"],
            'entities': [],
            'source': 'knowledge_base'
        })
        
        # Medication queries
        medication_examples = [
            "what medicine should i take",
            "any medication for this",
            "do you recommend any drugs",
            "what pills should i take",
            "medical treatment options",
            "prescription advice",
            "over the counter medicine"
        ]
        
        medical_intents.append({
            'intent': 'ask_medication',
            'examples': medication_examples,
            'responses': ["I cannot prescribe medications. Please consult with a healthcare professional for proper medication advice based on your specific condition."],
            'entities': [],
            'source': 'knowledge_base'
        })
        
        return medical_intents
    
    def create_rasa_nlu_data(self, all_intents):
        """Create Rasa NLU training data"""
        nlu_data = {
            'version': '3.1',
            'nlu': []
        }
        
        # Group examples by intent
        intent_examples = {}
        for intent_data in all_intents:
            intent_name = intent_data['intent']
            if intent_name not in intent_examples:
                intent_examples[intent_name] = []
            
            # Add examples with basic entity annotation
            for example in intent_data['examples']:
                # Simple entity annotation (in production, you'd use proper span annotation)
                annotated_example = f"- {example}"
                intent_examples[intent_name].append(annotated_example)
        
        # Create NLU entries
        for intent_name, examples in intent_examples.items():
            # Limit examples to avoid too large files
            unique_examples = list(set(examples))[:20]
            
            intent_entry = {
                'intent': intent_name,
                'examples': "\n".join(unique_examples)
            }
            nlu_data['nlu'].append(intent_entry)
        
        return nlu_data
    
    def create_rasa_domain(self, all_intents):
        """Create comprehensive Rasa domain file"""
        
        # Extract unique intents
        unique_intents = set()
        responses = {}
        
        for intent_data in all_intents:
            intent_name = intent_data['intent']
            unique_intents.add(intent_name)
            
            # Create response for each intent
            if intent_data.get('responses'):
                response_key = f"utter_{intent_name}"
                responses[response_key] = [{"text": intent_data['responses'][0]}]
        
        # Add specialized medical responses
        medical_responses = {
            "utter_ask_vaccine_info": [
                {"text": "💉 **Vaccine Information:**\n\nI can provide details about:\n• COVID-19 vaccines and boosters\n• Influenza (flu) vaccines\n• Hepatitis B vaccination\n• Routine childhood immunizations\n\nWhich specific vaccine would you like to know about?"}
            ],
            "utter_symptom_check": [
                {"text": "🔍 **Symptom Checker:**\n\nPlease describe your symptoms in detail, including:\n• What symptoms you're experiencing\n• How long you've had them\n• Severity level\n• Any triggers or patterns\n\nI can provide general information about common symptoms."}
            ],
            "utter_ask_diet_advice": [
                {"text": "🥗 **Diet & Nutrition Guidance:**\n\nI can offer general dietary advice for:\n• Diabetes management\n• Heart health\n• Weight management\n• Food allergies/intolerances\n• General healthy eating\n\nWhat specific dietary information do you need?"}
            ],
            "utter_ask_prevention": [
                {"text": "🛡️ **Disease Prevention:**\n\nI can share prevention strategies for:\n• Heart disease and stroke\n• Diabetes\n• Cancer\n• Infectious diseases\n• General wellness\n\nWhat specific prevention information are you looking for?"}
            ],
            "utter_ask_medication": [
                {"text": "💊 **Medication Notice:**\n\nI cannot prescribe medications or provide specific drug recommendations. Please consult with healthcare professionals for:\n• Proper diagnosis\n• Medication prescriptions\n• Dosage instructions\n• Side effect monitoring"}
            ],
            "utter_greet": [
                {"text": "Hello! I'm your comprehensive medical assistant. 🤖 I can help with symptom information, vaccine details, diet advice, disease prevention, and general health questions. How can I assist you today?"}
            ],
            "utter_goodbye": [
                {"text": "Thank you for consulting with me! Remember, I provide general health information only. Always consult healthcare professionals for medical advice. Stay healthy! 👋"}
            ],
            "utter_help": [
                {"text": "I can help you with:\n🔍 Symptom information\n💉 Vaccine details\n🥗 Diet and nutrition advice\n🛡️ Disease prevention tips\n🏥 General health information\n\nWhat would you like to know?"}
            ],
            "utter_emergency": [
                {"text": "🚨 **MEDICAL EMERGENCY ALERT** 🚨\n\nIf you're experiencing a medical emergency:\n• Call emergency services immediately\n• Go to the nearest hospital\n• Do not delay seeking help\n\nYour health and safety are the top priority! 🏥"}
            ]
        }
        
        responses.update(medical_responses)
        
        domain_data = {
            'version': '3.1',
            'intents': list(unique_intents) + [
                'greet', 'goodbye', 'help', 'emergency',
                'ask_vaccine_info', 'symptom_check', 'ask_diet_advice', 
                'ask_prevention', 'ask_medication'
            ],
            'entities': ['symptom', 'body_part', 'disease', 'treatment'],
            'slots': {
                'symptom_slot': {
                    'type': 'text',
                    'influence_conversation': True,
                    'mappings': [{'type': 'from_entity', 'entity': 'symptom'}]
                },
                'body_part_slot': {
                    'type': 'text',
                    'influence_conversation': True,
                    'mappings': [{'type': 'from_entity', 'entity': 'body_part'}]
                },
                'disease_slot': {
                    'type': 'text',
                    'influence_conversation': True,
                    'mappings': [{'type': 'from_entity', 'entity': 'disease'}]
                }
            },
            'responses': responses,
            'actions': [
                'action_provide_medical_info',
                'action_vaccine_info',
                'action_symptom_checker',
                'action_diet_advice',
                'action_disease_prevention',
                'action_emergency_check'
            ],
            'session_config': {
                'session_expiration_time': 60,
                'carry_over_slots_to_new_session': True
            }
        }
        
        return domain_data
    
    def create_rasa_stories(self, all_intents):
        """Create Rasa stories"""
        
        stories_data = {
            'version': '3.1',
            'stories': [
                {
                    'story': 'greet path',
                    'steps': [
                        {'intent': 'greet'},
                        {'action': 'utter_greet'}
                    ]
                },
                {
                    'story': 'goodbye path',
                    'steps': [
                        {'intent': 'goodbye'},
                        {'action': 'utter_goodbye'}
                    ]
                },
                {
                    'story': 'help path',
                    'steps': [
                        {'intent': 'help'},
                        {'action': 'utter_help'}
                    ]
                },
                {
                    'story': 'emergency path',
                    'steps': [
                        {'intent': 'emergency'},
                        {'action': 'utter_emergency'}
                    ]
                },
                {
                    'story': 'vaccine inquiry',
                    'steps': [
                        {'intent': 'ask_vaccine_info'},
                        {'action': 'utter_ask_vaccine_info'}
                    ]
                },
                {
                    'story': 'symptom check',
                    'steps': [
                        {'intent': 'symptom_check'},
                        {'action': 'utter_symptom_check'}
                    ]
                },
                {
                    'story': 'diet advice',
                    'steps': [
                        {'intent': 'ask_diet_advice'},
                        {'action': 'utter_ask_diet_advice'}
                    ]
                },
                {
                    'story': 'prevention info',
                    'steps': [
                        {'intent': 'ask_prevention'},
                        {'action': 'utter_ask_prevention'}
                    ]
                },
                {
                    'story': 'medication query',
                    'steps': [
                        {'intent': 'ask_medication'},
                        {'action': 'utter_ask_medication'}
                    ]
                }
            ]
        }
        
        # Add stories for dataset intents (limit to avoid too many stories)
        dataset_intents = [intent for intent in all_intents if intent.get('source') != 'knowledge_base']
        
        for intent_data in dataset_intents[:50]:  # Limit to 50 stories from datasets
            story_name = f"medical_{intent_data['intent']}"
            steps = [
                {'intent': intent_data['intent']},
                {'action': f"utter_{intent_data['intent']}"}
            ]
            
            stories_data['stories'].append({
                'story': story_name,
                'steps': steps
            })
        
        return stories_data
    
    def create_rasa_rules(self):
        """Create Rasa rules"""
        
        rules_data = {
            'version': '3.1',
            'rules': [
                {
                    'rule': 'Greet user',
                    'steps': [
                        {'intent': 'greet'},
                        {'action': 'utter_greet'}
                    ]
                },
                {
                    'rule': 'Say goodbye',
                    'steps': [
                        {'intent': 'goodbye'},
                        {'action': 'utter_goodbye'}
                    ]
                },
                {
                    'rule': 'Provide help',
                    'steps': [
                        {'intent': 'help'},
                        {'action': 'utter_help'}
                    ]
                },
                {
                    'rule': 'Emergency response',
                    'steps': [
                        {'intent': 'emergency'},
                        {'action': 'utter_emergency'}
                    ]
                }
            ]
        }
        
        return rules_data
    
    def save_medical_knowledge(self):
        """Save medical knowledge base to JSON"""
        knowledge_file = self.base_dir / "medical_knowledge.json"
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.medical_knowledge, f, indent=2)
        print(f"✅ Medical knowledge base saved to {knowledge_file}")
    
    def process_all_data(self):
        """Main method to process all data and create Rasa training files"""
        
        print("🏥 Starting Medical Data Processing...")
        print("=" * 60)
        
        # Load datasets
        datasets = self.load_all_datasets()
        
        all_intents = []
        intent_sources = {}
        
        # Process each dataset
        if 'chatbot' in datasets:
            print(f"\n📋 Processing chatbot data ({len(datasets['chatbot'])} rows)...")
            chatbot_intents = self.process_chatbot_data(datasets['chatbot'])
            all_intents.extend(chatbot_intents)
            intent_sources['chatbot'] = len(chatbot_intents)
            print(f"✅ Added {len(chatbot_intents)} intents from chatbot data")
        
        if 'conversations' in datasets:
            print(f"\n📋 Processing conversations data ({len(datasets['conversations'])} rows)...")
            conv_intents = self.process_conversations_data(datasets['conversations'])
            all_intents.extend(conv_intents)
            intent_sources['conversations'] = len(conv_intents)
            print(f"✅ Added {len(conv_intents)} intents from conversations data")
        
        if 'train' in datasets:
            print(f"\n📋 Processing train data ({len(datasets['train'])} rows)...")
            train_intents = self.process_train_test_data(datasets['train'], 'train')
            all_intents.extend(train_intents)
            intent_sources['train'] = len(train_intents)
            print(f"✅ Added {len(train_intents)} intents from train data")
        
        if 'test' in datasets:
            print(f"\n📋 Processing test data ({len(datasets['test'])} rows)...")
            test_intents = self.process_train_test_data(datasets['test'], 'test')
            all_intents.extend(test_intents)
            intent_sources['test'] = len(test_intents)
            print(f"✅ Added {len(test_intents)} intents from test data")
        
        # Add specialized medical intents
        print(f"\n📋 Adding specialized medical intents...")
        medical_intents = self.create_specialized_medical_intents()
        all_intents.extend(medical_intents)
        intent_sources['knowledge_base'] = len(medical_intents)
        print(f"✅ Added {len(medical_intents)} specialized medical intents")
        
        # Create Rasa training files
        print(f"\n📁 Creating Rasa training files...")
        nlu_data = self.create_rasa_nlu_data(all_intents)
        domain_data = self.create_rasa_domain(all_intents)
        stories_data = self.create_rasa_stories(all_intents)
        rules_data = self.create_rasa_rules()
        
        # Save files
        with open(self.data_dir / 'nlu.yml', 'w', encoding='utf-8') as f:
            yaml.dump(nlu_data, f, allow_unicode=True, sort_keys=False)
            
        with open(self.base_dir / 'domain.yml', 'w', encoding='utf-8') as f:
            yaml.dump(domain_data, f, allow_unicode=True, sort_keys=False)
            
        with open(self.data_dir / 'stories.yml', 'w', encoding='utf-8') as f:
            yaml.dump(stories_data, f, allow_unicode=True, sort_keys=False)
            
        with open(self.data_dir / 'rules.yml', 'w', encoding='utf-8') as f:
            yaml.dump(rules_data, f, allow_unicode=True, sort_keys=False)
        
        # Save medical knowledge
        self.save_medical_knowledge()
        
        # Print summary
        print(f"\n" + "=" * 60)
        print(f"✅ PROCESSING COMPLETE!")
        print(f"=" * 60)
        print(f"📊 Total intents created: {len(all_intents)}")
        print(f"\n📁 Source Breakdown:")
        for source, count in intent_sources.items():
            print(f"   • {source}: {count} intents")
        
        print(f"\n📁 Files created:")
        print(f"   - data/nlu.yml")
        print(f"   - domain.yml") 
        print(f"   - data/stories.yml")
        print(f"   - data/rules.yml")
        print(f"   - medical_knowledge.json")
        
        print(f"\n🎯 Your medical bot can now handle:")
        print(f"   💉 Vaccine information (COVID, flu, hepatitis B)")
        print(f"   🔍 Symptom checking and guidance")
        print(f"   🥗 Diet and nutrition advice (diabetes, heart health, celiac)")
        print(f"   🛡️ Disease prevention tips")
        print(f"   💊 Medication guidance (with proper disclaimers)")
        print(f"   🏥 General medical queries from your datasets")
        
        print(f"\n🚀 Next steps:")
        print(f"   1. Run: python train_medical_bot.py")
        print(f"   2. Then: rasa shell")
        
        return len(all_intents)

# Run the processor
if __name__ == "__main__":
    processor = MedicalDataProcessor()
    total_intents = processor.process_all_data()
    
    if total_intents > 0:
        print(f"\n🎉 Successfully processed {total_intents} medical intents!")
        print("Your medical bot training data is ready!")
    else:
        print("\n❌ No data was processed. Please check your dataset files.")