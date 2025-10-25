import os
import streamlit as st
from typing import Optional, List

try:
    from openai import OpenAI
    client = OpenAI()
    USE_NEW_SDK = True
    OPENAI_SDK_AVAILABLE = True
except Exception:
    try:
        import openai
        USE_NEW_SDK = False
        OPENAI_SDK_AVAILABLE = True
    except Exception:
        openai = None
        client = None
        USE_NEW_SDK = False
        OPENAI_SDK_AVAILABLE = False

APP_TITLE = "🩺 Your Care Pal (PH Based)"
DISCLAIMER = (
    "⚠️ I am not a medical professional. This is for general information only. "
    "For serious or emergency situations, please consult a licensed doctor or call local emergency services."
)

BASE_SYSTEM_PROMPT = f"""You are The Care Pal, a friendly basic health helper based in the Philippines.
Domain focus:
- Only cover common wellness topics: first aid tips, common illnesses (cold, flu, headache, stomach ache, minor injuries), nutrition/hydration, exercise, stress management.
- Avoid deep medical diagnosis and do not provide prescriptions or exact drug dosages.

Safety and disclaimers:
1) Always include this disclaimer at the start or end: "{DISCLAIMER}"
2) If a request involves prescriptions, dosages, experimental/dangerous procedures, or exact diagnoses, politely refuse and guide the user to a licensed professional.
3) For emergencies, tell the user to call 911 immediately.
4) If unsure, provide a safe fallback: "I'm not sure about that, but here's a safe general suggestion…"

Answer style:
- Use simple, everyday language. Prefer plain words (e.g., say "heart attack" not "myocardial infarction").
- Use short paragraphs or bullet lists, step-by-step when giving instructions.
- Be empathetic, supportive, and concise unless asked for more detail.
- Encourage safe, healthy habits and offer gentle reminders like "Take care of yourself!" or "Stay healthy!"

Philippine context:
- When giving nutrition advice, recommend Filipino foods and dishes (e.g., sinigang, adobo, bangus, tilapia, malunggay, kangkong, brown rice).
- For meal plans, suggest traditional Filipino breakfast (silog, tocino, longganisa), lunch (adobo, sinigang, tinola), and dinner options.
- Mention local ingredients like calamansi, bagoong, coconut oil, and tropical fruits.
- For exercise, consider Philippine climate and suggest indoor activities during hot weather.
- For hydration, mention buko juice (coconut water) as a natural electrolyte drink.
- Use Filipino terms when appropriate (e.g., "malunggay" for moringa, "kangkong" for water spinach).

Source guidance:
- Prefer general, widely accepted advice (e.g., WHO, Red Cross first aid basics, DOH Philippines health tips). Do not cite specific sources unless certain.
"""

PERSONAS = {
    "Clinic Nurse": "You speak like a calm, supportive clinic nurse. You reassure, avoid jargon, and give gentle, clear steps.",
    "Health Coach": "You speak like an encouraging health coach. You motivate with simple, actionable habits and checklists.",
    "School Counselor": "You speak like a warm school counselor. You emphasize mental well-being, stress management, and supportive tips."
}

BLOCKLIST_CATEGORIES = {
    "Medication specifics / prescribing": [
        "dosage", "dose", "mg", "milligram", "prescribe", "prescription",
        "antibiotic", "amoxicillin", "metformin", "insulin", "opioid",
    ],
    "High-risk domains": [
        "self-harm", "suicide", "kill myself", "overdose",
    ],
    "Diagnostic certainty": [
        "exact diagnosis", "what disease is this exactly",
    ],
    "Experimental/dangerous": [
        "inject", "iv drip at home", "home surgery", "stitches at home",
    ],
}

BLOCKLIST_RESPONSES = {
    "Medication specifics / prescribing": (
        f"{DISCLAIMER}\n\nI can’t provide prescriptions or dosage instructions. Prescription medicines should only be taken when they are prescribed specifically for you. "
        "Usually, clinicians choose a medicine and dose based on your age, weight, medical history, allergies, other medicines, and an in-person exam.\n\n"
        "Safe general steps you can consider: keep a brief symptoms log (start time, severity, what worsens/relieves), rest, hydrate, eat light meals, and use over-the-counter options only as directed on the product label. "
        "Avoid taking multiple products with the same active ingredient. If symptoms persist, worsen, or you notice red-flag signs, please see a licensed healthcare provider promptly."
    ),
    "High-risk domains": (
        f"{DISCLAIMER}\n\nI’m really sorry you’re going through this. I can’t help with self-harm or life-threatening situations. "
        "Please seek immediate help: call 911 right now. If you can, reach out to someone you trust nearby. "
        "If you are in immediate danger, try not to be alone and get urgent help."
    ),
    "Diagnostic certainty": (
        f"{DISCLAIMER}\n\nI can’t provide an exact diagnosis. A clinician would need a physical exam, history, and possibly tests. "
        "Consider keeping a symptoms log (onset, triggers, what helps) and see a licensed healthcare provider, especially if symptoms persist, worsen, or you notice red-flag signs."
    ),
    "Experimental/dangerous": (
        f"{DISCLAIMER}\n\nI can’t assist with dangerous or invasive procedures. Please do not attempt this at home. "
        "Keep the area clean, avoid actions that could worsen harm or infection, and seek care from a licensed healthcare professional. "
        "Call 911 if there is severe bleeding, breathing trouble, or loss of consciousness."
    ),
}

EMERGENCY_KEYWORDS = [
    "chest pain", "severe bleeding", "not breathing", "unconscious", "stroke", "heart attack",
    "can't breathe", "breathing trouble", "passed out", "fainted", "bleeding heavily", 
    "blood everywhere", "heart attack", "cardiac arrest", "choking", "severe allergic reaction",
    "anaphylaxis", "severe head injury", "spinal injury", "severe burn", "overdose"
]

def is_emergency(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in EMERGENCY_KEYWORDS)

def get_emergency_response(user_input: str) -> str:
    text = user_input.lower()
    em_num = "911"
    
    if "chest pain" in text or "heart attack" in text:
        return f"""{DISCLAIMER}

🚨 **CHEST PAIN/HEART ATTACK - EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**While waiting for help:**
- Have the person sit down and rest
- Loosen tight clothing
- If they have prescribed heart medication (like nitroglycerin), help them take it
- Stay with them and keep them calm
- If they become unconscious, start CPR if you know how

**DO NOT:**
- Drive them to the hospital yourself
- Give them aspirin unless specifically prescribed
- Leave them alone

**Time is critical - every minute counts!**"""
    
    elif "not breathing" in text or "can't breathe" in text or "breathing trouble" in text:
        return f"""{DISCLAIMER}

🚨 **BREATHING EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**While waiting for help:**
- Check if they're conscious and responsive
- If unconscious and not breathing, start CPR immediately
- If conscious but struggling to breathe:
  - Help them sit upright
  - Loosen tight clothing around neck/chest
  - Stay calm and reassure them
- If they have an inhaler (for asthma), help them use it

**DO NOT:**
- Panic or rush them
- Give them anything to eat or drink
- Leave them alone

**This is a life-threatening emergency!**"""
    
    elif "unconscious" in text or "passed out" in text or "fainted" in text:
        return f"""{DISCLAIMER}

🚨 **UNCONSCIOUS PERSON - EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**While waiting for help:**
- Check if they're breathing
- If breathing: place them on their side (recovery position)
- If NOT breathing: start CPR immediately
- Check for pulse
- Do NOT move them if you suspect spinal injury
- Stay with them and monitor their breathing

**Recovery Position:**
- Roll them onto their side
- Tilt head back slightly
- Bend top leg to keep them stable
- This prevents choking if they vomit

**DO NOT:**
- Try to wake them by shaking
- Give them anything to eat or drink
- Leave them alone

**This requires immediate medical attention!**"""
    
    elif "severe bleeding" in text or "bleeding heavily" in text or "blood everywhere" in text:
        return f"""{DISCLAIMER}

🚨 **SEVERE BLEEDING - EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**While waiting for help:**
- Apply direct pressure to the wound with clean cloth/towel
- If bleeding doesn't stop, apply more pressure
- Elevate the injured area above heart level (if possible)
- Do NOT remove objects stuck in the wound
- Keep pressure until help arrives

**If bleeding is from limb:**
- Apply pressure above the wound (between wound and heart)
- Use tourniquet only as last resort if bleeding won't stop

**DO NOT:**
- Remove objects from wound
- Use tourniquet unless absolutely necessary
- Panic - stay calm and focused

**Severe blood loss can be fatal quickly!**"""
    
    elif "stroke" in text:
        return f"""{DISCLAIMER}

🚨 **STROKE - EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**Remember FAST:**
- **F**ace: Is one side drooping?
- **A**rms: Can they raise both arms?
- **S**peech: Is speech slurred or strange?
- **T**ime: Time is critical - call immediately!

**While waiting for help:**
- Keep them calm and still
- Do NOT give them anything to eat or drink
- Note the time symptoms started
- If they become unconscious, place in recovery position

**DO NOT:**
- Drive them to hospital yourself
- Give them aspirin
- Wait to see if symptoms improve

**Every minute counts with stroke!**"""
    
    elif "choking" in text or "can't swallow" in text:
        return f"""{DISCLAIMER}

🚨 **CHOKING - EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**If person is conscious:**
- Encourage them to cough forcefully
- If coughing doesn't work, perform Heimlich maneuver
- Stand behind them, place hands above navel
- Give quick upward thrusts until object is expelled

**If person is unconscious:**
- Start CPR immediately
- Check mouth for visible object (remove if seen)
- Continue CPR until help arrives

**DO NOT:**
- Slap them on the back
- Give them anything to drink
- Leave them alone

**Choking can be fatal within minutes!**"""
    
    elif "severe allergic reaction" in text or "anaphylaxis" in text:
        return f"""{DISCLAIMER}

🚨 **SEVERE ALLERGIC REACTION - EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**While waiting for help:**
- If they have an EpiPen, help them use it immediately
- Help them lie down and elevate legs
- Loosen tight clothing
- Stay with them and monitor breathing
- If they become unconscious, start CPR

**Signs of severe reaction:**
- Difficulty breathing or swallowing
- Swelling of face, lips, tongue, or throat
- Rapid pulse, dizziness, or fainting
- Severe rash or hives

**DO NOT:**
- Give them anything to eat or drink
- Wait to see if symptoms improve
- Leave them alone

**This can be life-threatening quickly!**"""
    
    else:
        return f"""{DISCLAIMER}

🚨 **MEDICAL EMERGENCY**

**CALL {em_num} IMMEDIATELY!**

**While waiting for help:**
- Stay with the person
- Keep them calm and comfortable
- Do NOT give them anything to eat or drink
- Monitor their breathing and consciousness
- If they become unconscious, place in recovery position

**This requires immediate medical attention!**"""

def get_nutrition_advice(user_input: str) -> str:
    text = user_input.lower()
    
    weekly_plan = {
        "monday": {
            "breakfast": "Arroz caldo (rice porridge) with chicken, boiled egg, and calamansi",
            "lunch": "Grilled bangus (milkfish) with ensaladang talong, brown rice",
            "dinner": "Sinigang na hipon (shrimp soup) with kangkong and brown rice"
        },
        "tuesday": {
            "breakfast": "Tocino with garlic rice, fried egg, and atchara",
            "lunch": "Chicken adobo with steamed vegetables and brown rice",
            "dinner": "Ginataang gulay (vegetables in coconut milk) with grilled fish"
        },
        "wednesday": {
            "breakfast": "Champorado (chocolate rice porridge) with tuyo (dried fish)",
            "lunch": "Pancit bihon with mixed vegetables and lean meat",
            "dinner": "Tinola (chicken soup) with malunggay leaves and brown rice"
        },
        "thursday": {
            "breakfast": "Tapsilog (beef tapa, sinangag, itlog) with fresh tomatoes",
            "lunch": "Grilled tilapia with ensaladang mangga and brown rice",
            "dinner": "Pinakbet (mixed vegetables) with grilled pork and brown rice"
        },
        "friday": {
            "breakfast": "Longganisa with garlic rice, fried egg, and fresh fruits",
            "lunch": "Lumpiang sariwa (fresh spring rolls) with peanut sauce",
            "dinner": "Sinigang na baboy (pork soup) with vegetables and brown rice"
        },
        "saturday": {
            "breakfast": "Tocino with garlic rice, fried egg, and fresh mango",
            "lunch": "Grilled chicken inasal with atchara and brown rice",
            "dinner": "Kare-kare (oxtail stew) with bagoong and brown rice"
        },
        "sunday": {
            "breakfast": "Silog (garlic rice and egg) with your choice of meat",
            "lunch": "Lechon kawali with ensaladang talong and brown rice",
            "dinner": "Nilagang baka (beef soup) with vegetables and brown rice"
        }
    }
    
    hydration_tips = [
        "Drink 8-10 glasses of water daily (2-2.5 liters)",
        "Start your day with a glass of water",
        "Drink water before, during, and after exercise",
        "Include hydrating foods: watermelon, cucumber, oranges",
        "Limit caffeine and alcohol as they can dehydrate"
    ]
    
    healthy_foods = {
        "proteins": "Bangus (milkfish), tilapia, chicken, pork, beef, eggs, tokwa (tofu), monggo (mung beans)",
        "carbohydrates": "Brown rice, kamote (sweet potato), saba (banana), oats, whole grain bread, fruits",
        "vegetables": "Kangkong, malunggay, talong (eggplant), okra, ampalaya (bitter gourd), tomatoes, leafy greens",
        "fats": "Coconut oil, olive oil, nuts, seeds, fatty fish (bangus, tilapia), avocado",
        "dairy": "Fresh milk, keso (cheese), yogurt (in moderation)"
    }
    
    meal_plan_text = "**Weekly Healthy Meal Plan (Philippine Cuisine):**\n\n"
    for day, meals in weekly_plan.items():
        meal_plan_text += f"**{day.capitalize()}:**\n"
        meal_plan_text += f"**Breakfast:** {meals['breakfast']}\n"
        meal_plan_text += f"**Lunch:** {meals['lunch']}\n"
        meal_plan_text += f"**Dinner:** {meals['dinner']}\n\n"
    
    foods_text = "**Healthy Food Categories (Philippine Foods):**\n\n"
    for category, foods in healthy_foods.items():
        foods_text += f"**{category.capitalize()}:** {foods}\n"
    
    hydration_items = ["**Hydration Tips:**"] + [f"{tip}" for tip in hydration_tips]
    
    return format_sections(
        title="Nutrition & Hydration Guide",
        what_it_is="Comprehensive nutrition advice with weekly meal plans and healthy food recommendations for optimal health and wellness.",
        do_now=[
            "Plan your meals for the week using the provided meal plan",
            "Include a variety of colors in your meals (rainbow of fruits and vegetables)",
            "Eat regular meals and healthy snacks to maintain energy",
            "Stay hydrated throughout the day"
        ],
        watch_for=[
            "Signs of dehydration: dry mouth, dark urine, fatigue",
            "Food allergies or intolerances",
            "Sudden changes in appetite or weight"
        ],
        when_to_see=[
            "If you have specific dietary restrictions or allergies",
            "If you experience digestive issues with certain foods",
            "For personalized nutrition counseling"
        ],
        extra_notes=[
            meal_plan_text,
            foods_text,
            *hydration_items,
            "Remember: Balance is key - enjoy a variety of foods in moderation"
        ]
    )

def get_exercise_tips(user_input: str) -> str:
    text = user_input.lower()
    
    weight = None
    height = None
    
    import re
    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|pounds?|lbs?|lb)', text)
    if weight_match:
        weight_value = float(weight_match.group(1))
        if 'lb' in weight_match.group(0).lower():
            weight = weight_value * 0.453592
        else:
            weight = weight_value
    
    height_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:cm|m|feet?|ft|inches?|in)', text)
    if height_match:
        height_value = float(height_match.group(1))
        if 'cm' in height_match.group(0).lower():
            height = height_value / 100
        elif 'm' in height_match.group(0).lower():
            height = height_value
        elif 'ft' in height_match.group(0).lower() or 'feet' in height_match.group(0).lower():
            inches_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inches?|in)', text)
            if inches_match:
                inches = float(inches_match.group(1))
                height = height_value * 0.3048 + inches * 0.0254
            else:
                height = height_value * 0.3048
        elif 'in' in height_match.group(0).lower() or 'inches' in height_match.group(0).lower():
            height = height_value * 0.0254
    
    bmi_category = None
    if weight and height:
        bmi = weight / (height ** 2)
        if bmi < 18.5:
            bmi_category = "underweight"
        elif bmi < 25:
            bmi_category = "normal"
        elif bmi < 30:
            bmi_category = "overweight"
        else:
            bmi_category = "obese"
    
    if "weight loss" in text or "lose weight" in text or "burn fat" in text:
        if bmi_category == "overweight" or bmi_category == "obese":
            return format_sections(
                title="Weight Loss Exercise Plan",
                what_it_is="A safe, gradual approach to losing weight through exercise and healthy habits.",
                do_now=[
                    "Start with 30 minutes of moderate cardio 3-4 times per week (walking, cycling, swimming)",
                    "Add 2-3 strength training sessions per week to build muscle and boost metabolism",
                    "Begin with bodyweight exercises: squats, push-ups, planks, lunges",
                    "Include flexibility exercises: yoga or stretching for 10-15 minutes daily"
                ],
                watch_for=[
                    "Joint pain or excessive fatigue",
                    "Dizziness or feeling faint during exercise",
                    "Chest pain or difficulty breathing"
                ],
                when_to_see=[
                    "Any concerning symptoms during exercise",
                    "If you have heart conditions, diabetes, or other health issues"
                ],
                extra_notes=[
                    "Start slowly and gradually increase intensity",
                    "Aim for 150 minutes of moderate exercise per week",
                    "Combine with healthy eating for best results",
                    "Track your progress but don't obsess over the scale",
                    "💡 **For personalized advice, tell me your height and weight like:** 'I'm 70kg and 170cm' or 'I'm 5'8\" and 150lbs'"
                ]
            )
        else:
            return format_sections(
                title="Healthy Weight Management",
                what_it_is="Maintaining a healthy weight through balanced exercise and nutrition.",
                do_now=[
                    "Mix cardio and strength training for overall fitness",
                    "Try 30-45 minutes of moderate exercise most days",
                    "Include activities you enjoy: dancing, sports, hiking",
                    "Focus on building strength and endurance"
                ],
                watch_for=[
                    "Signs of overtraining: excessive fatigue, mood changes",
                    "Joint pain or injury"
                ],
                when_to_see=[
                    "Persistent pain or injury",
                    "If you have concerns about your weight or health"
                ],
                extra_notes=[
                    "Maintain a balanced approach to exercise and nutrition",
                    "Listen to your body and rest when needed"
                ]
            )
    
    elif "gain weight" in text or "build muscle" in text or "bulk up" in text:
        return format_sections(
            title="Muscle Building Exercise Plan",
            what_it_is="A structured approach to building muscle mass and strength safely.",
            do_now=[
                "Focus on compound exercises: squats, deadlifts, bench press, rows",
                "Start with 3-4 strength training sessions per week",
                "Use progressive overload: gradually increase weight or reps",
                "Include 1-2 days of light cardio for heart health"
            ],
            watch_for=[
                "Overtraining signs: excessive fatigue, poor sleep, mood changes",
                "Joint pain or injury from improper form"
            ],
            when_to_see=[
                "Persistent pain or injury",
                "If you have heart conditions or other health concerns"
            ],
            extra_notes=[
                "Proper form is more important than heavy weights",
                "Rest and recovery are crucial for muscle growth",
                "Combine with adequate protein intake",
                "Consider working with a trainer for proper technique",
                "💡 **For personalized advice, tell me your height and weight like:** 'I'm 70kg and 170cm' or 'I'm 5'8\" and 150lbs'"
            ]
        )
    
    elif "cardio" in text or "running" in text or "cycling" in text or "swimming" in text:
        return format_sections(
            title="Cardiovascular Exercise",
            what_it_is="Exercise that strengthens your heart and improves endurance.",
            do_now=[
                "Start with 20-30 minutes of moderate cardio 3-4 times per week",
                "Choose activities you enjoy: walking, running, cycling, swimming, dancing",
                "Warm up for 5-10 minutes before intense exercise",
                "Cool down and stretch after your workout"
            ],
            watch_for=[
                "Chest pain, dizziness, or difficulty breathing",
                "Excessive fatigue that doesn't improve with rest"
            ],
            when_to_see=[
                "Any concerning symptoms during exercise",
                "If you have heart conditions or breathing problems"
            ],
            extra_notes=[
                "Build up gradually - don't overdo it in the beginning",
                "Stay hydrated before, during, and after exercise",
                "Listen to your body and rest when needed"
            ]
        )
    
    elif "strength" in text or "weight training" in text or "gym" in text:
        return format_sections(
            title="Strength Training Basics",
            what_it_is="Exercise that builds muscle strength and bone density.",
            do_now=[
                "Start with bodyweight exercises: squats, push-ups, planks, lunges",
                "Focus on proper form before adding weight",
                "Work all major muscle groups: legs, chest, back, arms, core",
                "Rest 1-2 days between strength training sessions"
            ],
            watch_for=[
                "Sharp pain during exercise",
                "Excessive muscle soreness that lasts more than 3 days"
            ],
            when_to_see=[
                "Persistent pain or injury",
                "If you have joint problems or other health conditions"
            ],
            extra_notes=[
                "Proper form prevents injury and maximizes results",
                "Start light and gradually increase weight",
                "Include both pushing and pulling movements",
                "Don't skip leg day - work all muscle groups"
            ]
        )
    
    elif "beginner" in text or "start" in text or "new to exercise" in text:
        return format_sections(
            title="Getting Started with Exercise",
            what_it_is="A beginner-friendly approach to starting a regular exercise routine.",
            do_now=[
                "Start with 10-15 minutes of light activity daily",
                "Try walking, gentle stretching, or basic bodyweight exercises",
                "Set realistic goals: aim for 3 days per week initially",
                "Choose activities you enjoy to build the habit"
            ],
            watch_for=[
                "Excessive fatigue or muscle soreness",
                "Any pain or discomfort during exercise"
            ],
            when_to_see=[
                "If you have health concerns or chronic conditions",
                "Persistent pain or unusual symptoms"
            ],
            extra_notes=[
                "Consistency is more important than intensity",
                "Listen to your body and progress gradually",
                "Consider consulting a fitness professional for guidance",
                "Remember: any movement is better than no movement",
                "💡 **For personalized advice, tell me your height and weight like:** 'I'm 70kg and 170cm' or 'I'm 5'8\" and 150lbs'"
            ]
        )
    
    else:
        
        if bmi_category == "underweight":
            return format_sections(
                title="Exercise & Nutrition Plan for Healthy Weight Gain",
                what_it_is="Based on your measurements, you're in the underweight range. Focus on building healthy muscle mass and increasing calorie intake safely.",
                do_now=[
                    "Strength training 3-4 times per week: squats, push-ups, planks, lunges",
                    "Light cardio 2-3 times per week: walking, swimming, cycling",
                    "Eat 5-6 small meals throughout the day",
                    "Include protein with every meal: eggs, chicken, fish, beans, nuts"
                ],
                watch_for=[
                    "Excessive fatigue or feeling weak",
                    "Loss of appetite or difficulty eating",
                    "Joint pain during strength training"
                ],
                when_to_see=[
                    "If you have difficulty gaining weight despite following the plan",
                    "If you experience persistent fatigue or weakness"
                ],
                extra_notes=[
                    "Focus on strength training to build muscle mass",
                    "Eat calorie-dense foods: nuts, avocados, olive oil, whole grains",
                    "Stay hydrated and get adequate sleep for muscle recovery",
                    "Consider working with a nutritionist for personalized meal planning"
                ]
            )
        elif bmi_category == "normal":
            return format_sections(
                title="Exercise & Nutrition Plan for Healthy Maintenance",
                what_it_is="Based on your measurements, you're in the healthy weight range. Maintain your current routine with balanced exercise and nutrition.",
                do_now=[
                    "Mix cardio and strength training: 3-4 times per week",
                    "Include variety: running, cycling, swimming, weight training",
                    "Eat balanced meals with all food groups",
                    "Stay hydrated: 8-10 glasses of water daily"
                ],
                watch_for=[
                    "Signs of overtraining: excessive fatigue, mood changes",
                    "Weight fluctuations outside your normal range"
                ],
                when_to_see=[
                    "If you notice significant weight changes",
                    "If you have concerns about your fitness routine"
                ],
                extra_notes=[
                    "Maintain your current healthy habits",
                    "Include fruits, vegetables, lean proteins, and whole grains",
                    "Listen to your body and adjust intensity as needed",
                    "Regular health check-ups to monitor your progress"
                ]
            )
        elif bmi_category == "overweight":
            return format_sections(
                title="Exercise & Nutrition Plan for Healthy Weight Management",
                what_it_is="Based on your measurements, you're in the overweight range. Focus on moderate cardio and strength training with balanced nutrition.",
                do_now=[
                    "Moderate cardio 4-5 times per week: brisk walking, cycling, swimming",
                    "Strength training 2-3 times per week: bodyweight exercises",
                    "Eat smaller, more frequent meals",
                    "Focus on lean proteins, vegetables, and whole grains"
                ],
                watch_for=[
                    "Joint pain during exercise",
                    "Dizziness or excessive fatigue",
                    "Difficulty maintaining the exercise routine"
                ],
                when_to_see=[
                    "If you experience persistent joint pain",
                    "If you have heart conditions or other health concerns"
                ],
                extra_notes=[
                    "Start with low-impact activities to protect your joints",
                    "Reduce portion sizes and avoid processed foods",
                    "Stay consistent with your routine for best results",
                    "Consider working with a fitness professional for guidance"
                ]
            )
        elif bmi_category == "obese":
            return format_sections(
                title="Exercise & Nutrition Plan for Safe Weight Management",
                what_it_is="Based on your measurements, you're in the obese range. Start with low-impact activities and consult a healthcare provider before beginning.",
                do_now=[
                    "Low-impact cardio: walking, swimming, cycling (start with 10-15 minutes)",
                    "Gentle strength training: light weights, resistance bands",
                    "Eat regular, balanced meals with portion control",
                    "Stay hydrated and get adequate sleep"
                ],
                watch_for=[
                    "Chest pain, dizziness, or difficulty breathing",
                    "Joint pain or excessive fatigue",
                    "Any concerning symptoms during exercise"
                ],
                when_to_see=[
                    "Before starting any exercise program",
                    "If you experience any concerning symptoms",
                    "For personalized nutrition and exercise guidance"
                ],
                extra_notes=[
                    "Start slowly and gradually increase intensity",
                    "Focus on whole foods and avoid processed foods",
                    "Consider working with healthcare professionals",
                    "Set realistic goals and celebrate small victories"
                ]
            )
        
        return format_sections(
            title="General Exercise Guidelines",
            what_it_is="Safe, effective exercise recommendations for overall health and fitness.",
            do_now=[
                "Aim for 150 minutes of moderate exercise per week",
                "Include both cardio and strength training",
                "Start with activities you enjoy: walking, dancing, sports",
                "Warm up before and cool down after exercise"
            ],
            watch_for=[
                "Chest pain, dizziness, or difficulty breathing",
                "Excessive fatigue or muscle soreness",
                "Joint pain or injury"
            ],
            when_to_see=[
                "Any concerning symptoms during exercise",
                "If you have health conditions or concerns"
            ],
            extra_notes=[
                "Start slowly and gradually increase intensity",
                "Stay hydrated and listen to your body",
                "Consistency is key - even 10 minutes is better than nothing",
                "💡 **For personalized advice, tell me your height and weight like:** 'I'm 70kg and 170cm' or 'I'm 5'8\" and 150lbs'"
            ]
        )

def get_disallowed_category(text: str):
    t = text.lower()
    for category, keywords in BLOCKLIST_CATEGORIES.items():
        if any(k in t for k in keywords):
            return category
    return None

def is_disallowed(text: str) -> bool:
    return get_disallowed_category(text) is not None

def build_system_prompt(persona: str) -> str:
    persona_instr = PERSONAS.get(persona, "")
    base_prompt = BASE_SYSTEM_PROMPT + "\n\nPersona instructions: " + persona_instr
    
    # Add user's name if available
    if hasattr(st, 'session_state') and st.session_state.get('user_name'):
        base_prompt += f"\n\nUser's name: {st.session_state.user_name}. Use their name when appropriate to make responses more personal and friendly."
    
    return base_prompt

def format_sections(title: str, what_it_is: str, do_now: List[str], watch_for: List[str], when_to_see: List[str], extra_notes: Optional[List[str]] = None) -> str:
    disclaimer = DISCLAIMER
    parts = []
    if title:
        parts.append(f"**{title}**")
    if what_it_is:
        parts.append(f"\n**What it is:**\n{what_it_is}")
    if do_now:
        bullets = "\n".join([f"- {item}" for item in do_now])
        parts.append(f"\n**Do now**\n{bullets}")
    if watch_for:
        bullets = "\n".join([f"- {item}" for item in watch_for])
        parts.append(f"\n**Watch for**\n{bullets}")
    if when_to_see:
        bullets = "\n".join([f"- {item}" for item in when_to_see])
        parts.append(f"\n**When to see a doctor**\n{bullets}")
    if extra_notes:
        bullets = "\n".join([f"- {item}" for item in extra_notes])
        parts.append(f"\n**Notes**\n{bullets}")
    parts.append(f"\n{disclaimer}")
    return "\n\n".join(parts)

def get_greeting_response(user_input: str) -> str:
    text = user_input.lower()
    
    import re
    name_patterns = [
        r"my name is ([a-zA-Z]+)",
        r"i'm ([a-zA-Z]+)",
        r"i am ([a-zA-Z]+)",
        r"call me ([a-zA-Z]+)",
        r"i'm called ([a-zA-Z]+)",
        r"name's ([a-zA-Z]+)",
        r"my name's ([a-zA-Z]+)",
        r"i go by ([a-zA-Z]+)",
        r"you can call me ([a-zA-Z]+)"
    ]
    
    name = None
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).capitalize()
            st.session_state.user_name = name
            break
    
    from datetime import datetime
    import pytz
    
    # Use Philippines timezone for consistent greetings
    try:
        ph_tz = pytz.timezone('Asia/Manila')
        current_hour = datetime.now(ph_tz).hour
    except:
        # Fallback to local time if pytz not available
        current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        time_greeting = "Good morning"
    elif 12 <= current_hour < 17:
        time_greeting = "Good afternoon"
    elif 17 <= current_hour < 21:
        time_greeting = "Good evening"
    else:
        time_greeting = "Hello"
    
    if name:
        return f"""{time_greeting}, {name}! 👋

I'm Your Care Pal, your friendly wellness companion. I can help with:

• First aid tips for minor injuries  
• Common illnesses (colds, headaches, etc.)  
• Nutrition/hydration advice  
• Exercise recommendations based on your weight/height  
• Stress management techniques  

What can I help you with today, {name}?

{DISCLAIMER}"""
    else:
        return f"""{time_greeting}! 👋

I'm Your Care Pal, your friendly wellness companion. I can help with:

• First aid tips for minor injuries  
• Common illnesses (colds, headaches, etc.)  
• Nutrition/hydration advice  
• Exercise recommendations based on your weight/height  
• Stress management techniques  

What's your name? And what can I help you with today?

{DISCLAIMER}"""

def extract_name_from_input(user_input: str) -> str:
    text = user_input.lower()
    import re
    
    if re.search(r'\d+\s*(kg|kgs|pounds?|lbs?|lb|cm|m|feet?|ft|inches?|in)', text):
        return None
    
    name_patterns = [
        r"my name is ([a-zA-Z]+)",
        r"i'm ([a-zA-Z]+)",
        r"i am ([a-zA-Z]+)",
        r"call me ([a-zA-Z]+)",
        r"i'm called ([a-zA-Z]+)",
        r"name's ([a-zA-Z]+)",
        r"my name's ([a-zA-Z]+)",
        r"i go by ([a-zA-Z]+)",
        r"you can call me ([a-zA-Z]+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).capitalize()
            st.session_state.user_name = name
            return name
    return None


def local_response(user_input: str, persona: str) -> str:
    text = user_input.lower()

    greeting_words = ["hello", "hey", "good morning", "good afternoon", "good evening", "greetings"]
    if any(word in text for word in greeting_words) or text.strip() == "hi":
        return get_greeting_response(user_input)

    if any(word in text for word in ["chest pain", "not breathing", "unconscious", "severe bleeding"]):
        return get_emergency_response(user_input)

    if "cut" in text or "wound" in text:
        return format_sections(
            title="Small cut or minor wound",
            what_it_is="A small break in the skin that may bleed a little and usually heals on its own with basic care.",
            do_now=[
                "Wash your hands.",
                "Gently clean the cut with clean water.",
                "Apply gentle pressure with a clean cloth to stop bleeding.",
                "Cover with a clean bandage.",
            ],
            watch_for=[
                "Redness spreading, pus, or increasing pain/swelling (possible infection).",
                "Bleeding that doesn’t stop after 10 minutes of pressure.",
            ],
            when_to_see=[
                "The cut is deep, very dirty, or edges are far apart.",
                "You haven’t had a tetanus shot in the last 5–10 years.",
            ],
        )

    if "cold" in text or "cough" in text:
        return format_sections(
            title="Common cold or cough",
            what_it_is="A mild viral illness causing stuffy/runny nose, sore throat, or cough.",
            do_now=[
                "Drink plenty of water and rest well.",
                "Warm soups, steam, or a humidifier may help.",
            ],
            watch_for=[
                "High fever, chest pain, trouble breathing, or confusion.",
                "Symptoms lasting more than a week or getting worse.",
            ],
            when_to_see=[
                "Breathing difficulties, severe chest pain, or persistent high fever.",
            ],
            extra_notes=[
                "Over-the-counter options may help; follow the product label exactly.",
                "Do not mix products with the same active ingredient.",
                "If pregnant/breastfeeding, for children, or with chronic conditions, ask a clinician before taking any medication.",
            ],
        )

    if "stress" in text or "anxiety" in text or "panic attacks" in text:
        return format_sections(
            title="Stress or anxiety",
            what_it_is="A common response to pressure; short-term strategies can help you feel calmer.",
            do_now=[
                "Take slow, deep breaths for 1–2 minutes.",
                "Stretch or do light exercise; take a short walk.",
                "Write down worries and one small action you can take.",
                "Talk to a supportive friend or family member.",
            ],
            watch_for=[
                "Panic attacks, unrelenting anxiety, or thoughts of self-harm.",
            ],
            when_to_see=[
                "Symptoms that persist or interfere with daily life.",
            ],
        )

    if "fever" in text or "high temperature" in text:
        return format_sections(
            title="Fever (non-emergency care)",
            what_it_is="A temporary rise in body temperature, often due to infection.",
            do_now=[
                "Drink plenty of fluids (water, oral rehydration, broths).",
                "Rest and wear light clothing; keep the room comfortably cool.",
                "Sponge with lukewarm water if uncomfortable (avoid ice-cold baths).",
            ],
            watch_for=[
                "Very high fever, stiff neck, confusion, severe headache, breathing trouble, chest pain, persistent vomiting.",
            ],
            when_to_see=[
                "Fever lasting more than 2–3 days or if you feel very unwell.",
            ],
            extra_notes=[
                "You may consider over-the-counter fever reducers; follow the product label exactly.",
                "Do not mix products with the same active ingredient.",
                "If pregnant/breastfeeding, for children, or with chronic conditions, check with a clinician first.",
            ],
        )

    if "sore throat" in text or "throat pain" in text:
        return format_sections(
            title="Sore throat",
            what_it_is="Irritation or pain in the throat, often from a viral infection.",
            do_now=[
                "Warm saltwater gargles (1/2 tsp salt in a cup of warm water).",
                "Warm fluids (soups, tea with honey) and good hydration.",
                "Use a humidifier or take steamy showers.",
                "Throat lozenges or sprays can help; follow the label directions.",
            ],
            watch_for=[
                "Severe pain, drooling, trouble breathing, rash, or high fever.",
            ],
            when_to_see=[
                "Symptoms lasting more than a few days or worsening.",
            ],
            extra_notes=[
                "Do not mix products with the same active ingredient.",
                "If pregnant/breastfeeding, for children, or with chronic conditions, ask a clinician before taking any medication.",
            ],
        )

    if "headache" in text or "migraine" in text or "head pain" in text:
        return format_sections(
            title="Common headache",
            what_it_is="Head pain often related to tension, dehydration, or screen strain.",
            do_now=[
                "Hydrate and have regular, balanced meals.",
                "Rest in a quiet, dim room; take screen breaks and mind your posture.",
                "Manage stress with brief breathing or stretching breaks.",
            ],
            watch_for=[
                "Worst-ever sudden headache, head injury, fever with stiff neck, confusion, weakness/numbness, vision changes.",
            ],
            when_to_see=[
                "Headaches that get worse, keep returning, or don’t respond to simple care.",
            ],
            extra_notes=[
                "Over-the-counter pain relievers may help; follow the product label exactly.",
                "Do not mix products with the same active ingredient.",
                "If pregnant/breastfeeding, for children, or with chronic conditions, check with a clinician first.",
            ],
        )

    if "stomach ache" in text or "stomachache" in text or "abdominal pain" in text:
        return format_sections(
            title="Mild stomach ache",
            what_it_is="Abdominal discomfort that often improves with rest and light diet.",
            do_now=[
                "Sip clear fluids (water or oral rehydration).",
                "Try small, bland meals (crackers, toast, rice, bananas).",
                "Rest and avoid strenuous activity.",
            ],
            watch_for=[
                "Severe pain, persistent vomiting, blood in stool/vomit, black stool, fever with pain, or worsening pain.",
            ],
            when_to_see=[
                "Pain that lasts more than a day or is severe.",
            ],
        )

    if "diarrhea" in text or "loose stools" in text:
        return format_sections(
            title="Diarrhea",
            what_it_is="Frequent, loose stools that can cause dehydration.",
            do_now=[
                "Hydrate with water or oral rehydration solution (small, frequent sips).",
                "Eat bland foods (bananas, rice, applesauce, toast) as tolerated.",
                "Wash hands and clean surfaces to prevent spread.",
            ],
            watch_for=[
                "Blood or black stool, high fever, signs of dehydration (very dry mouth, dizziness).",
            ],
            when_to_see=[
                "Symptoms lasting more than 2–3 days or any red-flag symptoms.",
            ],
        )

    if "burn" in text or "scald" in text:
        return format_sections(
            title="Minor burn or scald (first-degree)",
            what_it_is="Red, painful skin without blisters.",
            do_now=[
                "Cool the area under cool running water for 10–20 minutes (not ice).",
                "Remove tight items (rings/watches) near the area before swelling.",
                "Cover loosely with a clean, non‑stick dressing.",
            ],
            watch_for=[
                "Large area, worsening pain, or signs of infection.",
            ],
            when_to_see=[
                "Face, hands, genitals, or a large area; or if blisters form.",
            ],
        )

    if "nosebleed" in text or "nose bleed" in text:
        return format_sections(
            title="Nosebleed",
            what_it_is="Bleeding from inside the nose, often from dryness or minor injury.",
            do_now=[
                "Sit upright, tilt head slightly forward.",
                "Pinch the soft part of the nose for 10–15 minutes without releasing.",
                "Spit out blood; avoid swallowing.",
            ],
            watch_for=[
                "Bleeding that doesn’t stop after 20 minutes, dizziness, or if on blood thinners.",
            ],
            when_to_see=[
                "Frequent nosebleeds or after a significant injury.",
            ],
        )

    if "faint" in text or "passed out" in text or "syncope" in text:
        return format_sections(
            title="Fainting (syncope)",
            what_it_is="Brief loss of consciousness often from low blood pressure or dehydration.",
            do_now=[
                "Lay the person on their back and raise legs if safe.",
                "Loosen tight clothing and ensure fresh air.",
                "When awake, offer sips of water if not nauseated.",
            ],
            watch_for=[
                "Head injury, chest pain, shortness of breath, confusion, or repeated fainting.",
            ],
            when_to_see=[
                "Any head injury or if episodes repeat or don’t recover quickly.",
            ],
        )

    if "dehydration" in text:
        return format_sections(
            title="Dehydration",
            what_it_is="Not enough fluids in the body; can cause dizziness or fatigue.",
            do_now=[
                "Sip oral rehydration solution or water regularly.",
                "Rest in a cool area and avoid heat.",
            ],
            watch_for=[
                "Very dry mouth, minimal urine, dizziness/fainting, confusion.",
            ],
            when_to_see=[
                "Severe symptoms or if unable to keep fluids down.",
            ],
        )

    if "food poisoning" in text or ("vomit" in text and "diarrhea" in text):
        return format_sections(
            title="Suspected food poisoning",
            what_it_is="Gastro symptoms after eating contaminated food.",
            do_now=[
                "Hydrate with water or oral rehydration solution.",
                "Rest and reintroduce bland foods slowly.",
            ],
            watch_for=[
                "Blood in stool/vomit, black stool, high fever, signs of dehydration.",
            ],
            when_to_see=[
                "Symptoms lasting more than 1–2 days or any red‑flag symptoms.",
            ],
        )

    if "dengue" in text:
        return format_sections(
            title="Dengue prevention (Philippines)",
            what_it_is="Viral illness spread by Aedes mosquitoes.",
            do_now=[
                "Eliminate standing water (flower pots, containers).",
                "Use mosquito repellent and wear long sleeves/pants.",
                "Use screens or nets; keep surroundings clean.",
            ],
            watch_for=[
                "High fever, severe headache, eye pain, joint/muscle pain, bleeding gums or nose.",
            ],
            when_to_see=[
                "Any warning signs or persistent high fever; seek medical care.",
            ],
        )

    if "heat exhaustion" in text or ("heat" in text and "dizzy" in text):
        return format_sections(
            title="Heat exhaustion",
            what_it_is="Overheating with heavy sweating and weakness.",
            do_now=[
                "Move to a cool place; loosen clothing.",
                "Sip water or oral rehydration solution; cool the skin with wet cloths or a fan.",
            ],
            watch_for=[
                "Confusion, fainting, very high temperature, or no sweating (possible heat stroke).",
            ],
            when_to_see=[
                "Symptoms not improving within 30 minutes or any red‑flag signs.",
            ],
        )

    if any(word in text for word in ["nutrition", "diet", "food", "eating", "eat", "meal", "breakfast", "lunch", "dinner", "snack", "hydrate", "water", "healthy food", "meal plan"]):
        return get_nutrition_advice(user_input)

    if any(word in text for word in ["exercise", "workout", "fitness", "gym", "weight loss", "lose weight", "gain weight", "muscle", "cardio", "strength training"]):
        return get_exercise_tips(user_input)
    
    import re
    if re.search(r'\d+\s*(kg|kgs|pounds?|lbs?|lb|cm|m|feet?|ft|inches?|in)', text):
        return get_exercise_tips(user_input)

    return format_sections(
        title="General wellness",
        what_it_is="I couldn’t fully understand your question, so here are safe general tips that often help with mild concerns.",
        do_now=["Drink water.", "Get enough rest.", "Eat balanced meals."],
        watch_for=["Symptoms that persist, worsen, or include red‑flag signs (severe pain, trouble breathing, confusion)."],
        when_to_see=["Any serious or persistent symptoms."],
    )

def openai_chat(messages, model_name):
    if not OPENAI_SDK_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OpenAI API not configured")
    if USE_NEW_SDK:
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.4,
        )
        return resp.choices[0].message.content
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        resp = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            temperature=0.4,
        )
        return resp["choices"][0]["message"]["content"]

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🩺")
    st.title(APP_TITLE)
    st.caption("I am your friendly wellness companion: simple first-aid steps, common-illness tips, nutrition and exercise advice, and stress guidance. Works offline with a safe rule-based fallback.")

    with st.expander("DISCLAIMER:", expanded=True):
        st.write(DISCLAIMER)

    st.sidebar.header("Settings")
    
    # Check for API key in environment variables or Streamlit secrets
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        # Try to get from Streamlit secrets
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            api_key = None
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.sidebar.success("✅ OpenAI API key found!")
    else:
        st.sidebar.warning("⚠️ No OpenAI API key found. App will run in offline mode.")
    
    if os.getenv("OPENAI_API_KEY"):
        st.sidebar.markdown("**🤖 AI Mode:** Enhanced responses with OpenAI")
    else:
        st.sidebar.markdown("**📚 Offline Mode:** Rule-based responses")

    model_name = "gpt-4o-mini"
    persona = st.sidebar.selectbox("Persona", list(PERSONAS.keys()), index=0)
    st.sidebar.caption("Note: Persona applies only with an API key; offline mode ignores persona.")
    st.sidebar.markdown("---")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = build_system_prompt(persona)
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "name_acknowledgment" not in st.session_state:
        st.session_state.name_acknowledgment = None
    # Utilities
    if st.sidebar.button("Reset chat"):
        st.session_state.messages = []
        st.session_state.user_name = None
        st.session_state.name_acknowledgment = None
        st.rerun()
    st.sidebar.subheader("Examples")
    st.sidebar.write("- First aid for a small cut")
    st.sidebar.write("- Tips to relieve a cold")
    st.sidebar.write("- Healthy snacks for studying")
    st.sidebar.write("- Quick stress-relief exercises")

    if st.session_state.system_prompt != build_system_prompt(persona):
        st.session_state.system_prompt = build_system_prompt(persona)

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    user_input = st.chat_input("Say hello or ask a health/wellness question...")
    if user_input:
        extracted_name = extract_name_from_input(user_input)
        
        if extracted_name and not any(word in user_input.lower() for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"]):
            name_acknowledgment = f"Nice to meet you, {extracted_name}! I'll remember your name for our conversation. "
            st.session_state.name_acknowledgment = name_acknowledgment
        
        if is_emergency(user_input):
            emergency_response = get_emergency_response(user_input)
            with st.chat_message("assistant"):
                st.markdown(emergency_response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": emergency_response
            })
            st.stop()

        greeting_words = ["hello", "hey", "good morning", "good afternoon", "good evening", "greetings"]
        if any(word in user_input.lower() for word in greeting_words) or user_input.lower().strip() == "hi":
            greeting_response = get_greeting_response(user_input)
            with st.chat_message("assistant"):
                st.markdown(greeting_response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": greeting_response
            })
            st.stop()

        if is_disallowed(user_input):
            category = get_disallowed_category(user_input)
            refusal = BLOCKLIST_RESPONSES.get(category, f"{DISCLAIMER}\n\nI can’t assist with that request. Please consult a licensed healthcare provider.")
            with st.chat_message("assistant"):
                st.markdown(refusal)
            st.session_state.messages.append({"role": "assistant", "content": refusal})
            st.stop()

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        if not os.getenv("OPENAI_API_KEY") or not OPENAI_SDK_AVAILABLE:
            reply = local_response(user_input, persona)
            
            if st.session_state.get('name_acknowledgment'):
                reply = st.session_state.name_acknowledgment + reply
                st.session_state.name_acknowledgment = None
            
            elif st.session_state.get('user_name'):
                if "What can I help you with today" not in reply and "How can I help you" not in reply and "What's your name" not in reply:
                    if not reply.startswith(f"Good ") and not reply.startswith("Hello") and not reply.startswith("Hi"):
                        reply = f"Hi {st.session_state.user_name}! {reply}"
            
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.stop()

        messages = [{"role": "system", "content": st.session_state.system_prompt}]
        for m in st.session_state.messages:
            if m["role"] in ("user", "assistant"):
                messages.append(m)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = openai_chat(messages, model_name)
                except Exception:
                    reply = local_response(user_input, persona)

                st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    st.markdown("---")
    st.caption("Built for CPELE230 Finals by Red Ocampo — Your Care Pal")

if __name__ == "__main__":
    main()
