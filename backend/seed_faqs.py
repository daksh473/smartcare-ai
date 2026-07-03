import sqlite3

DB_PATH = "smartcare.db"

def seed_regional_faqs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if we already seeded non-english
    cursor.execute("SELECT COUNT(*) FROM knowledge_base WHERE language != 'en'")
    if cursor.fetchone()[0] > 0:
        print("Already seeded.")
        return

    faqs = [
        # Hindi
        ("डिलीवरी में कितना समय लगता है?", "स्टैंडर्ड डिलीवरी में 3-5 दिन लगते हैं।", "shipping", "hi"),
        ("क्या आप रिफंड देते हैं?", "हां, 30 दिनों के भीतर रिफंड संभव है।", "refund", "hi"),
        ("भुगतान के तरीके क्या हैं?", "हम क्रेडिट कार्ड और यूपीआई स्वीकार करते हैं।", "payment", "hi"),
        ("पासवर्ड कैसे बदलें?", "अपने अकाउंट सेटिंग में जाएं।", "account", "hi"),
        ("क्या आपके उत्पाद शाकाहारी हैं?", "हां, 100% शाकाहारी।", "product", "hi"),
        
        # Hinglish
        ("Delivery mein kitna time lagta hai?", "Standard delivery takes 3-5 days.", "shipping", "hin"),
        ("Refund kaise milega?", "30 days ke andar return kar sakte hain.", "refund", "hin"),
        ("Payment options kya hain?", "Cards aur UPI accepted hain.", "payment", "hin"),
        ("Account password reset kaise karein?", "Login page pe 'Forgot Password' click karein.", "account", "hin"),
        ("Products vegan hain kya?", "Haan, 100% vegan aur cruelty-free hain.", "product", "hin"),
        
        # Tamil
        ("டெலிவரிக்கு எவ்வளவு நேரம் ஆகும்?", "சாதாரண டெலிவரிக்கு 3-5 நாட்கள் ஆகும்.", "shipping", "ta"),
        ("நான் எப்படி பணத்தை திரும்பப் பெறுவது?", "30 நாட்களுக்குள் பொருட்களை திருப்பி அனுப்பலாம்.", "refund", "ta"),
        ("கட்டண முறைகள் என்ன?", "நாங்கள் கிரெடிட் கார்டு மற்றும் UPI ஏற்றுக்கொள்கிறோம்.", "payment", "ta"),
        ("கடவுச்சொல்லை மாற்றுவது எப்படி?", "உங்கள் கணக்கு அமைப்புகளுக்குச் செல்லவும்.", "account", "ta"),
        ("உங்கள் தயாரிப்புகள் சைவமானவையா?", "ஆம், 100% சைவமானவை.", "product", "ta"),
        
        # Bengali
        ("ডেলিভারি হতে কতক্ষণ সময় লাগে?", "স্ট্যান্ডার্ড ডেলিভারি ৩-৫ দিন সময় নেয়।", "shipping", "bn"),
        ("রিফান্ড কীভাবে পাব?", "৩০ দিনের মধ্যে পণ্য ফেরত দেওয়া যাবে।", "refund", "bn"),
        ("পেমেন্ট অপশন কি কি?", "আমরা কার্ড এবং ইউপিআই গ্রহণ করি।", "payment", "bn"),
        ("পাসওয়ার্ড কীভাবে পরিবর্তন করব?", "আপনার অ্যাকাউন্ট সেটিংসে যান।", "account", "bn"),
        ("আপনার পণ্যগুলো কি ভেগান?", "হ্যাঁ, ১০০% ভেগান।", "product", "bn"),
        
        # Telugu
        ("డెలివరీకి ఎంత సమయం పడుతుంది?", "సాధారణ డెలివరీకి 3-5 రోజులు పడుతుంది.", "shipping", "te"),
        ("నేను రీఫండ్ ఎలా పొందగలను?", "30 రోజుల లోపు వస్తువులను తిరిగి ఇవ్వవచ్చు.", "refund", "te"),
        ("చెల్లింపు పద్ధతులు ఏమిటి?", "మేము క్రెడిట్ కార్డు మరియు UPI ఆమోదిస్తాము.", "payment", "te"),
        ("పాస్వర్డ్ మార్చడం ఎలా?", "మీ ఖాతా సెట్టింగ్లకు వెళ్లండి.", "account", "te"),
        ("మీ ఉత్పత్తులు శాకాహారమా?", "అవును, 100% శాకాహారం.", "product", "te")
    ]
    
    cursor.executemany('''
        INSERT INTO knowledge_base (question, answer, category, language, usage_count)
        VALUES (?, ?, ?, ?, 0)
    ''', faqs)
    
    conn.commit()
    conn.close()
    print("Seeded regional FAQs.")

if __name__ == "__main__":
    seed_regional_faqs()
