from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
import json
import os
import random
from pathlib import Path
import re

class ActionSessionStart(Action):
    """Action to handle session start"""
    
    def name(self) -> Text:
        return "action_session_start"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        # Send welcome message
        dispatcher.utter_message(
            text="👋 Welcome to your Medical Assistant! I can help with:\n\n"
                 "• Symptom information and guidance 🔍\n"
                 "• Vaccine details and schedules 💉\n" 
                 "• Diet and nutrition advice 🥗\n"
                 "• Disease prevention tips 🛡️\n"
                 "• General health information 🏥\n\n"
                 "How can I assist you with your health concerns today?"
        )
        
        return [SessionStarted(), ActionExecuted("action_listen")]

class ActionProvideMedicalInfo(Action):
    """Provide general medical information with enhanced responses"""
    
    def name(self) -> Text:
        return "action_provide_medical_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Load medical knowledge
        knowledge = self.load_medical_knowledge()
        
        # Get entities from the message
        symptoms = list(tracker.get_latest_entity_values("symptom") or [])
        diseases = list(tracker.get_latest_entity_values("disease") or [])
        body_parts = list(tracker.get_latest_entity_values("body_part") or [])
        treatments = list(tracker.get_latest_entity_values("treatment") or [])
        
        user_message = tracker.latest_message.get('text', '').lower()
        
        # Check for specific conditions in the message
        if any(word in user_message for word in ['rash', 'itching', 'skin']):
            symptoms.append('rash')
        if any(word in user_message for word in ['antibiotic', 'medicine', 'medication']):
            treatments.append('antibiotic')
        
        response = ""
        
        if symptoms:
            response += "🔍 **Symptom Information**\n\n"
            for symptom in symptoms[:3]:  # Limit to 3 symptoms
                if symptom in knowledge['symptoms']:
                    info = knowledge['symptoms'][symptom]
                    response += f"**{symptom.title()}**:\n"
                    response += f"• {info['description']}\n"
                    response += f"• Possible causes: {', '.join(info['possible_causes'][:2])}\n"
                    response += f"• Immediate care: {', '.join(info['first_aid'][:2])}\n"
                    response += f"• When to see doctor: {info['when_to_see_doctor']}\n\n"
                else:
                    response += f"**{symptom.title()}**: General symptom information - monitor and consult a doctor if persistent.\n\n"
        
        if diseases:
            response += "\n🏥 **Condition Information**\n\n"
            for disease in diseases[:2]:
                if disease in knowledge.get('disease_prevention', {}).get('specific', {}):
                    prevention_info = knowledge['disease_prevention']['specific'][disease]
                    response += f"**{disease.title()}**:\n"
                    response += f"• Prevention: {prevention_info}\n"
                    response += "• Consultation: Please see a healthcare provider for diagnosis and treatment.\n\n"
        
        if treatments:
            response += "\n💊 **Treatment Information**\n\n"
            if 'antibiotic' in treatments:
                response += "**Antibiotics**:\n"
                response += "• Must be prescribed by a healthcare professional\n"
                response += "• Complete the full course as directed\n"
                response += "• Don't share antibiotics with others\n"
                response += "• Report any side effects to your doctor\n\n"
        
        if not response:
            response = (
                "I understand you have health concerns. Please describe:\n\n"
                "• Your specific symptoms\n" 
                "• How long you've had them\n"
                "• Any other relevant details\n\n"
                "This will help me provide more accurate information."
            )
        else:
            response += "⚠️ *This is general health information. Always consult healthcare professionals for medical advice.*"
        
        dispatcher.utter_message(text=response)
        
        # Set slots for future context
        slots = []
        if symptoms:
            slots.append(SlotSet("symptom_slot", symptoms[0]))
        if diseases:
            slots.append(SlotSet("disease_slot", diseases[0]))
            
        return slots

class ActionVaccineInfo(Action):
    """Provide comprehensive vaccine information"""
    
    def name(self) -> Text:
        return "action_vaccine_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        knowledge = self.load_medical_knowledge()
        vaccines = knowledge['vaccinations']
        
        message = tracker.latest_message.get('text', '').lower()
        response = "💉 **Vaccine Information Center**\n\n"
        
        # Check for specific vaccine mentions with better matching
        if any(word in message for word in ['covid', 'corona', 'sars']):
            vax_info = vaccines['covid_19']
            response += "**COVID-19 Vaccines** 🦠\n"
            response += f"• **Types**: {', '.join(vax_info['types'])}\n"
            response += f"• **Schedule**: {vax_info['schedule']}\n"
            response += f"• **Common side effects**: {', '.join(vax_info['side_effects'])}\n"
            response += f"• **Effectiveness**: {vax_info['effectiveness']}\n"
            response += "• **Recommendation**: CDC recommends staying up-to-date with boosters\n\n"
        
        elif any(word in message for word in ['flu', 'influenza']):
            vax_info = vaccines['influenza']
            response += "**Influenza (Flu) Vaccine** 🤧\n"
            response += f"• **Recommendation**: {vax_info['recommendation']}\n"
            response += f"• **Types**: {', '.join(vax_info['types'])}\n"
            response += f"• **Best timing**: {vax_info['best_time']}\n"
            response += "• **Importance**: Reduces flu severity and prevents complications\n\n"
        
        elif any(word in message for word in ['hepatitis', 'hep b']):
            vax_info = vaccines['hepatitis_b']
            response += "**Hepatitis B Vaccine** 🩺\n"
            response += f"• **Schedule**: {vax_info['schedule']}\n"
            response += f"• **Recommended for**: {', '.join(vax_info['recommended_for'][:3])}\n"
            response += f"• **Effectiveness**: {vax_info['effectiveness']}\n"
            response += "• **Protection**: Prevents liver infection and long-term complications\n\n"
        
        else:
            response += "**Available Vaccine Information**:\n"
            response += "• **COVID-19** - mRNA and protein-based options\n"
            response += "• **Influenza (Flu)** - Annual seasonal protection\n" 
            response += "• **Hepatitis B** - 3-dose series for liver protection\n"
            response += "• **Other routine vaccines** (MMR, Tdap, etc.)\n\n"
            response += "Which specific vaccine would you like detailed information about?"
        
        response += "📋 **General Vaccine Guidance**:\n"
        response += "• Discuss with your healthcare provider about recommended vaccines\n"
        response += "• Keep a vaccination record\n"
        response += "• Report any adverse reactions\n"
        response += "• Stay informed about booster recommendations\n\n"
        
        response += "⚠️ *Vaccine recommendations may vary based on age, health conditions, and location. Consult healthcare providers for personalized advice.*"
        
        dispatcher.utter_message(text=response)
        return [SlotSet("last_topic", "vaccines")]

class ActionSymptomChecker(Action):
    """Provide comprehensive symptom checking guidance"""
    
    def name(self) -> Text:
        return "action_symptom_checker"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        knowledge = self.load_medical_knowledge()
        symptoms = list(tracker.get_latest_entity_values("symptom") or [])
        
        response = "🔍 **Symptom Assessment Guide**\n\n"
        
        if symptoms:
            response += "**Based on your reported symptoms**:\n\n"
            for symptom in symptoms[:4]:  # Limit to 4 symptoms
                if symptom in knowledge['symptoms']:
                    info = knowledge['symptoms'][symptom]
                    response += f"**{symptom.title()}**:\n"
                    response += f"• Description: {info['description']}\n"
                    response += f"• Self-care: {', '.join(info['first_aid'][:2])}\n"
                    response += f"• Medical attention: {info['when_to_see_doctor']}\n\n"
                else:
                    response += f"**{symptom.title()}**: Monitor and track this symptom. Note any changes.\n\n"
            
            response += "**Next Steps**:\n"
            response += "• Monitor symptom severity and duration\n"
            response += "• Note any new or worsening symptoms\n"
            response += "• Keep a symptom diary if persistent\n"
            response += "• Seek medical advice for proper evaluation\n\n"
        else:
            response += "**Please describe your symptoms for assessment**:\n\n"
            response += "📝 **Include details about**:\n"
            response += "• Specific symptoms you're experiencing\n"
            response += "• When they started and how long they've lasted\n"
            response += "• Severity (mild, moderate, severe)\n"
            response += "• Any triggers or patterns you've noticed\n"
            response += "• Other symptoms occurring together\n\n"
            response += "💡 **Example**: 'I've had fever and headache for 2 days, with body aches.'\n\n"
        
        response += "🚨 **RED FLAG - Seek IMMEDIATE Medical Attention for**:\n"
        response += "• Chest pain or pressure\n• Difficulty breathing\n• Severe bleeding\n• Sudden weakness or numbness\n"
        response += "• Confusion or loss of consciousness\n• Severe pain anywhere\n• High fever with stiff neck\n"
        response += "• Suicidal or homicidal thoughts\n\n"
        
        response += "⚠️ *This symptom checker provides general guidance only. It is not a substitute for professional medical evaluation, diagnosis, or treatment.*"
        
        dispatcher.utter_message(text=response)
        return [SlotSet("symptom_slot", symptoms[0] if symptoms else None)]

class ActionDietAdvice(Action):
    """Provide comprehensive diet and nutrition advice"""
    
    def name(self) -> Text:
        return "action_diet_advice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        knowledge = self.load_medical_knowledge()
        diets = knowledge['diet_plans']
        message = tracker.latest_message.get('text', '').lower()
        
        response = "🥗 **Nutrition & Dietary Guidance**\n\n"
        
        if any(word in message for word in ['diabet', 'blood sugar', 'sugar']):
            diet_info = diets['diabetes']
            response += "**Diabetes-Friendly Diet** 🩸\n"
            response += f"• **Focus**: {diet_info['focus']}\n"
            response += f"• **Foods to emphasize**: {', '.join(diet_info['foods_to_eat'][:4])}\n"
            response += f"• **Foods to limit**: {', '.join(diet_info['foods_to_limit'][:3])}\n"
            response += f"• **Meal timing**: {diet_info['meal_timing']}\n"
            response += "• **Key tips**: Balance carbohydrates, monitor portions, stay consistent\n\n"
        
        elif any(word in message for word in ['heart', 'cardio', 'cholesterol', 'blood pressure']):
            diet_info = diets['heart_health']
            response += "**Heart-Healthy Diet** ❤️\n"
            response += f"• **Focus**: {diet_info['focus']}\n"
            response += f"• **Beneficial foods**: {', '.join(diet_info['foods_to_eat'][:4])}\n"
            response += f"• **Foods to minimize**: {', '.join(diet_info['foods_to_avoid'][:3])}\n"
            response += f"• **Lifestyle integration**: {diet_info['lifestyle']}\n"
            response += "• **Additional benefits**: Supports healthy weight and blood pressure\n\n"
        
        elif any(word in message for word in ['weight', 'obesity', 'overweight', 'bmi']):
            diet_info = diets['weight_management']
            response += "**Weight Management Nutrition** ⚖️\n"
            response += f"• **Basic principle**: {diet_info['principle']}\n"
            response += f"• **Key strategies**: {', '.join(diet_info['recommendations'][:3])}\n"
            response += f"• **Helpful tips**: {', '.join(diet_info['tips'][:2])}\n"
            response += "• **Sustainable approach**: Focus on long-term habits, not quick fixes\n\n"
        
        elif any(word in message for word in ['celiac', 'gluten']):
            diet_info = diets['celiac_disease']
            response += "**Gluten-Free Diet for Celiac Disease** 🌾\n"
            response += f"• **Essential focus**: {diet_info['focus']}\n"
            response += f"• **Safe foods**: {', '.join(diet_info['foods_to_eat'][:4])}\n"
            response += f"• **Strictly avoid**: {', '.join(diet_info['foods_to_avoid'][:3])}\n"
            response += f"• **Critical consideration**: {diet_info['important']}\n"
            response += "• **Additional note**: Requires careful label reading and kitchen practices\n\n"
        
        else:
            response += "**Specialized Dietary Guidance Available**:\n"
            response += "• **Diabetes management** - Blood sugar control\n"
            response += "• **Heart health** - Cholesterol and blood pressure focus\n"
            response += "• **Weight management** - Healthy weight achievement\n"
            response += "• **Celiac disease** - Strict gluten-free approach\n"
            response += "• **General healthy eating** - Balanced nutrition\n\n"
            response += "Which specific dietary area would you like information about?"
        
        response += "📋 **Universal Healthy Eating Principles**:\n"
        response += "• Fill half your plate with fruits and vegetables\n"
        response += "• Choose whole grains over refined grains\n"
        response += "• Include lean protein sources\n"
        response += "• Stay well hydrated with water\n"
        response += "• Limit processed foods and added sugars\n"
        response += "• Practice mindful eating and portion awareness\n\n"
        
        response += "⚠️ *For personalized dietary plans, consult a registered dietitian or nutritionist who can consider your individual health needs and preferences.*"
        
        dispatcher.utter_message(text=response)
        return [SlotSet("last_topic", "diet")]

class ActionDiseasePrevention(Action):
    """Provide comprehensive disease prevention information"""
    
    def name(self) -> Text:
        return "action_disease_prevention"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        knowledge = self.load_medical_knowledge()
        prevention = knowledge['disease_prevention']
        message = tracker.latest_message.get('text', '').lower()
        
        response = "🛡️ **Disease Prevention & Wellness Strategies**\n\n"
        
        response += "**Essential Prevention Practices** 🌟\n"
        for i, tip in enumerate(prevention['general'][:8], 1):
            response += f"{i}. {tip}\n"
        
        response += "\n**Condition-Specific Prevention**\n\n"
        
        if any(word in message for word in ['diabet', 'blood sugar']):
            response += "**Diabetes Prevention** 🩸\n"
            response += f"{prevention['specific']['diabetes']}\n"
            response += "• **Key focus**: Maintain healthy weight through diet and exercise\n"
            response += "• **Monitoring**: Regular blood sugar checks if at risk\n"
            response += "• **Lifestyle**: Balanced nutrition and physical activity\n\n"
        
        elif any(word in message for word in ['heart', 'cardio', 'cholesterol']):
            response += "**Heart Disease Prevention** ❤️\n"
            response += f"{prevention['specific']['heart_disease']}\n"
            response += "• **Critical factors**: Blood pressure and cholesterol management\n"
            response += "• **Lifestyle**: Regular exercise and smoke-free environment\n"
            response += "• **Diet**: Low sodium, healthy fats, plenty of fruits/vegetables\n\n"
        
        elif any(word in message for word in ['cancer']):
            response += "**Cancer Prevention** 🎗️\n"
            response += f"{prevention['specific']['cancer']}\n"
            response += "• **Primary prevention**: Avoid tobacco and limit alcohol\n"
            response += "• **Early detection**: Regular screenings as recommended\n"
            response += "• **Healthy habits**: Sun protection and balanced nutrition\n\n"
        
        elif any(word in message for word in ['infection', 'virus', 'bacteria']):
            response += "**Infectious Disease Prevention** 🦠\n"
            response += f"{prevention['specific']['infections']}\n"
            response += "• **Hygiene**: Proper handwashing and food safety\n"
            response += "• **Immunization**: Stay up-to-date with vaccinations\n"
            response += "• **Awareness**: Avoid close contact when sick\n\n"
        
        else:
            response += "**Major Areas of Prevention**:\n"
            response += "• **Diabetes** - Weight management and healthy lifestyle\n"
            response += "• **Heart Disease** - Blood pressure control and exercise\n"
            response += "• **Cancer** - Avoid carcinogens and regular screening\n"
            response += "• **Infections** - Hygiene and immunization\n\n"
            response += "Which specific prevention area interests you?"
        
        response += "💡 **Proactive Health Maintenance**:\n"
        response += "• Schedule regular health check-ups\n"
        response += "• Know your family health history\n"
        response += "• Stay current with age-appropriate screenings\n"
        response += "• Maintain mental and emotional wellness\n"
        response += "• Build healthy relationships and support systems\n\n"
        
        response += "🌟 *Prevention is the most effective healthcare strategy. Small, consistent healthy choices create significant long-term benefits!*"
        
        dispatcher.utter_message(text=response)
        return [SlotSet("last_topic", "prevention")]

class ActionEmergencyCheck(Action):
    """Enhanced emergency situation detection and response"""
    
    def name(self) -> Text:
        return "action_emergency_check"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        emergency_keywords = [
            'emergency', 'urgent', 'critical', 'immediate', '911', 'hospital now',
            'chest pain', 'difficulty breathing', 'severe bleeding', 'unconscious',
            'stroke', 'heart attack', 'choking', 'seizure', 'poisoning',
            'can\'t breathe', 'dying', 'suicide', 'kill myself', 'severe pain'
        ]
        
        message = tracker.latest_message.get('text', '').lower()
        
        emergency_detected = any(keyword in message for keyword in emergency_keywords)
        
        if emergency_detected:
            dispatcher.utter_message(
                text="🚨 **MEDICAL EMERGENCY ALERT** 🚨\n\n"
                     "**IMMEDIATE ACTION REQUIRED**:\n\n"
                     "📞 **Call Emergency Services Now**:\n"
                     "• Dial 911 (US) or your local emergency number\n"
                     "• Clearly state your emergency and location\n"
                     "• Follow dispatcher instructions\n\n"
                     "🏥 **Go to Nearest Hospital**:\n"
                     "• Do not drive yourself if impaired\n"
                     "• Have someone take you or call ambulance\n"
                     "• Bring identification and insurance information\n\n"
                     "⚠️ **Do Not Delay**:\n"
                     "• Every minute counts in emergencies\n"
                     "• Your health and safety are paramount\n"
                     "• Professional medical care is essential\n\n"
                     "**You are not alone - help is available immediately!**"
            )
        else:
            # Regular health guidance
            dispatcher.utter_message(
                text="For non-emergency health concerns, I'm here to provide information and guidance. "
                     "If your situation becomes urgent, don't hesitate to seek immediate medical care."
            )
        
        return [SlotSet("emergency_detected", emergency_detected)]

class ActionFallback(Action):
    """Handle unrecognized queries and provide helpful guidance"""
    
    def name(self) -> Text:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(
            text="I'm not sure I understand. As your medical assistant, I can help with:\n\n"
                 "• **Symptom information** 🔍\n"
                 "• **Vaccine details** 💉\n" 
                 "• **Diet and nutrition** 🥗\n"
                 "• **Disease prevention** 🛡️\n"
                 "• **General health questions** 🏥\n\n"
                 "Could you rephrase your question or ask about one of these topics?"
        )
        
        return []

    def load_medical_knowledge(self):
        """Load medical knowledge from JSON file with enhanced error handling"""
        knowledge_file = Path("medical_knowledge.json")
        try:
            if knowledge_file.exists():
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge = json.load(f)
                    # Ensure all required sections exist
                    if 'symptoms' not in knowledge:
                        knowledge['symptoms'] = {}
                    if 'vaccinations' not in knowledge:
                        knowledge['vaccinations'] = {}
                    if 'diet_plans' not in knowledge:
                        knowledge['diet_plans'] = {}
                    if 'disease_prevention' not in knowledge:
                        knowledge['disease_prevention'] = {'general': [], 'specific': {}}
                    return knowledge
            else:
                # Create basic structure if file doesn't exist
                return self.create_basic_knowledge_base()
        except Exception as e:
            print(f"Error loading medical knowledge: {e}")
            return self.create_basic_knowledge_base()

    def create_basic_knowledge_base(self):
        """Create a basic medical knowledge base as fallback"""
        return {
            'symptoms': {
                'fever': {
                    'description': 'Elevated body temperature above normal',
                    'possible_causes': ['Infection', 'Inflammation'],
                    'first_aid': ['Rest', 'Hydration', 'Cool compresses'],
                    'when_to_see_doctor': 'If above 104°F or lasting more than 3 days'
                }
            },
            'vaccinations': {
                'covid_19': {
                    'types': ['mRNA vaccines', 'Protein subunit'],
                    'schedule': 'Primary series + boosters',
                    'side_effects': ['Pain at injection site', 'Fatigue'],
                    'effectiveness': 'High effectiveness against severe disease'
                }
            },
            'diet_plans': {
                'diabetes': {
                    'focus': 'Blood sugar control',
                    'foods_to_eat': ['Non-starchy vegetables', 'Lean proteins'],
                    'foods_to_limit': ['Sugary drinks', 'Refined carbs'],
                    'meal_timing': 'Regular meals throughout day'
                }
            },
            'disease_prevention': {
                'general': [
                    'Regular hand washing',
                    'Balanced diet',
                    'Regular exercise',
                    'Adequate sleep'
                ],
                'specific': {
                    'diabetes': 'Maintain healthy weight and exercise regularly',
                    'heart_disease': 'No smoking and control blood pressure'
                }
            }
        }