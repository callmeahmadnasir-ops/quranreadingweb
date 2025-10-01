import streamlit as st
import requests
import json
import sqlite3
import base64

st.set_page_config(
    page_title='Quran Recitation Videos', 
    page_icon='🕌',
    layout='wide',
    initial_sidebar_state='auto'
)

# Sidebar navigation
page = st.sidebar.radio('Navigation', ['Quran Reader'])

if page == 'Quran Reader':
    st.title('Quran Reader')
    
    # Load Google Fonts and add responsive CSS
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700&family=Scheherazade+New:wght@400;700&family=Noto+Naskh+Arabic:wght@400;700&family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
            .stMarkdown p {
                font-size: 14px !important;
                line-height: 1.8 !important;
            }
            div[data-testid="stMarkdownContainer"] div {
                padding: 8px !important;
            }
            .stAudio {
                width: 100% !important;
            }
        }
        /* Better spacing on mobile */
        .stDivider {
            margin: 1rem 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.title('Controls')
    
    surah_list = requests.get("http://api.alquran.cloud/v1/surah").json()["data"]
    
    surah_names = [f"{s['number']}: {s['name']} ({s['englishName']})" for s in surah_list]
    
    chosen_surah = st.sidebar.selectbox('Choose a Surah', surah_names)
    
    selected_surah_num = chosen_surah.split(":")[0]
    
    reciter_options = {
    'Alafasy': 'Alafasy_128kbps',
    'Abdul Basit (Murattal)': 'Abdul_Basit_Murattal_192kbps',
    'Husary': 'Husary_128kbps',
    'Husary (Mujawwad)': 'Husary_Mujawwad_128kbps',
    'Minshawy (Murattal)': 'Minshawy_Murattal_128kbps',
    'Minshawy (Mujawwad)': 'Minshawy_Mujawwad_128kbps',
    'Muhammad Jibreel': 'Muhammad_Jibreel_128kbps',
    'Saood ash-Shuraym': 'Saood_ash-Shuraym_128kbps',
    'Ghamadi': 'Ghamadi_40kbps',
    'Hudhaify': 'Hudhaify_128kbps',
    'Sudais': 'Abdurrahmaan_As-Sudais_192kbps',
    'Abu Bakr Shatri': 'Abu_Bakr_Ash-Shaatree_128kbps',
    'Maher Al Muaiqly': 'MaherAlMuaiqly128kbps',
    'Muhammad Ayyub': 'Muhammad_Ayyoub_128kbps',
    'Nasser Alqatami': 'Nasser_Alqatami_128kbps',
    'Sahl Yassin': 'Sahl_Yassin_128kbps',
    'Yasser Dosari': 'Yasser_Ad-Dussary_128kbps'
    }
    
    reciter_name = st.sidebar.selectbox('Choose Reciter', list(reciter_options.keys()))
    reciter = reciter_options[reciter_name]
    
    translation = st.sidebar.selectbox('Choose Translation', [
        'Ahmed Ali',
        'Jalandhry', 
        'Jawadi',
        'Junagarhi',
        'Kanzuliman',
        'Maududi',
        'Najafi',
        'Qadri',
        'Muhammad Taqi Usmani',
        'Sayyid Qutb',
        'Urdu Word by Word'
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Font Settings")
    
    arabic_font = st.sidebar.selectbox('Arabic Font', [
        'Amiri',
        'Scheherazade New',
        'Noto Naskh Arabic',
        'Cairo',
        'Arial',
        'Times New Roman'
    ])
    arabic_font_size = st.sidebar.slider('Arabic Font Size', 16, 48, 24)
    
    urdu_font = st.sidebar.selectbox('Urdu Font', [
        'Noto Nastaliq Urdu',
        'Amiri',
        'Cairo',
        'Arial',
        'Tahoma',
        'Verdana'
    ])
    urdu_font_size = st.sidebar.slider('Urdu Font Size', 12, 32, 16)
    
    arabic_display_mode = st.sidebar.selectbox('Arabic Display Mode', [
        'Standard Text (Uthmani)',
        'Imlaei Script',
        'Word by Word (QPC Nastaleeq)',
        'Word by Word (IndoPak Nastaleeq)',
        'Word Images (Calligraphy)',
        'Tajweed Images (Colored)'
    ])
    
    show_translation = st.sidebar.checkbox('Show Translation', value=True)
    
    st.sidebar.markdown("---")
    show_surah_info = st.sidebar.checkbox('Show Surah Information', value=False)
    
    st.sidebar.markdown("---")
    show_tafsir = st.sidebar.checkbox('Show Tafsir', value=False)
    
    show_matching_ayahs = st.sidebar.checkbox('Show Matching Ayahs', value=False)
    
    if show_matching_ayahs:
        matching_choice = st.sidebar.selectbox('Matching Type', ['Similar Meaning', 'Similar Words'], index=0)
    
    if show_tafsir:
        tafsir_choice = st.sidebar.selectbox('Choose Tafsir', [
            'Bayan-ul-Quran',
            'Tafseer Ibn-e-Kaseer',
            'Tafsir As-Saadi',
            'Tazkiru Quran',
            'Tafsir Fe Zalul Quran (Syed Qutb)'
        ])
    recitation_url = f"https://api.alquran.cloud/v1/surah/{selected_surah_num}/ar.alafasy"
    
    recitation_response = requests.get(recitation_url).json()
    
    # Load Tafsir data if needed
    tafsir_data = {}
    if show_tafsir:
        tafsir_files = {
            'Bayan-ul-Quran': 'bayan-ul-quran-simple.json',
            'Tafseer Ibn-e-Kaseer': 'tafseer-ibn-e-kaseer-urdu.json',
            'Tafsir As-Saadi': 'tafsir-as-saadi.json',
            'Tazkiru Quran': 'tazkiru-quran-ur.json',
            'Tafsir Fe Zalul Quran (Syed Qutb)': 'tafsir-fe-zalul-quran-syed-qatab.json'
        }
        tafsir_file = tafsir_files[tafsir_choice]
        with open(tafsir_file, 'r', encoding='utf-8') as f:
            tafsir_data = json.load(f)
    
    # Load Matching Ayahs data if needed
    matching_data = {}
    if show_matching_ayahs:
        try:
            with open('matching-ayah.json', 'r', encoding='utf-8') as f:
                matching_data = json.load(f)
        except Exception as e:
            st.sidebar.warning(f"Could not load matching ayahs data: {str(e)}")
    
    # Load Arabic text from local file
    arabic_ayahs = []
    with open('quran-uthmani.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 3 and parts[0] == selected_surah_num:
                surah_num = int(parts[0])
                ayah_num = int(parts[1])
                # EveryAyah.com audio URL format with selected reciter
                audio_url = f"http://everyayah.com/data/{reciter}/{surah_num:03d}{ayah_num:03d}.mp3"
                
                arabic_ayahs.append({
                    'numberInSurah': ayah_num,
                    'text': parts[2],
                    'audio': audio_url
                })
    
    if show_translation:
        # Load translation from local file
        translation_ayahs = []
        
        if translation == 'Urdu Word by Word':
            # Load word-by-word JSON
            with open('urud-wbw.json', 'r', encoding='utf-8') as f:
                wbw_data = json.load(f)
            
            # Group words by ayah
            ayah_words = {}
            for key, word in wbw_data.items():
                parts = key.split(':')
                if len(parts) == 3 and parts[0] == selected_surah_num:
                    ayah_num = int(parts[1])
                    if ayah_num not in ayah_words:
                        ayah_words[ayah_num] = []
                    ayah_words[ayah_num].append(word)
            
            # Create translation ayahs with joined words
            for ayah_num in sorted(ayah_words.keys()):
                translation_ayahs.append({
                    'numberInSurah': ayah_num,
                    'text': ' | '.join(ayah_words[ayah_num])
                })
        elif translation == 'Sayyid Qutb':
            # Load Sayyid Qutb JSON translation
            with open('urdu-sayyid-qatab-simple.json', 'r', encoding='utf-8') as f:
                qutb_data = json.load(f)
            
            for key, value in qutb_data.items():
                parts = key.split(':')
                if len(parts) == 2 and parts[0] == selected_surah_num:
                    translation_ayahs.append({
                        'numberInSurah': int(parts[1]),
                        'text': value['t']
                    })
        else:
            # Load regular translation from text file
            translation_map = {
                'Ahmed Ali': 'ur.ahmedali.txt',
                'Jalandhry': 'ur.jalandhry.txt',
                'Jawadi': 'ur.jawadi.txt',
                'Junagarhi': 'ur.junagarhi.txt',
                'Kanzuliman': 'ur.kanzuliman.txt',
                'Maududi': 'ur.maududi.txt',
                'Najafi': 'ur.najafi.txt',
                'Qadri': 'ur.qadri.txt',
                'Muhammad Taqi Usmani': 'urd-muhammadtaqiusm.txt'
            }
            
            filename = translation_map.get(translation)
            
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 3 and parts[0] == selected_surah_num:
                        translation_ayahs.append({
                            'numberInSurah': int(parts[1]),
                            'text': parts[2]
                        })
    else:
        translation_ayahs = [None] * len(arabic_ayahs)
    
    st.subheader(chosen_surah)
    
    # Display Surah Information if enabled
    if show_surah_info:
        with open('surah-info-ur.json', 'r', encoding='utf-8') as f:
            surah_info_data = json.load(f)
        
        if selected_surah_num in surah_info_data:
            info = surah_info_data[selected_surah_num]
            st.markdown(f"### {info['surah_name']}")
            # Apply font styling to surah info
            styled_text = f"<div style='font-family: \"{urdu_font}\", serif; font-size: {urdu_font_size}px;'>{info['text']}</div>"
            st.markdown(styled_text, unsafe_allow_html=True)
            st.markdown("---")
    
    # Load word data based on display mode
    word_images_data = {}
    word_text_data = {}
    imlaei_data = {}
    tajweed_images_data = {}
    
    if arabic_display_mode == 'Word Images (Calligraphy)':
        with open('black-images-word-by-word.json', 'r', encoding='utf-8') as f:
            word_images_data = json.load(f)
    elif arabic_display_mode == 'Tajweed Images (Colored)':
        with open('tajweed-images-old.json', 'r', encoding='utf-8') as f:
            tajweed_images_data = json.load(f)
    elif arabic_display_mode == 'Word by Word (QPC Nastaleeq)':
        with open('qpc-nastaleeq.json', 'r', encoding='utf-8') as f:
            word_text_data = json.load(f)
    elif arabic_display_mode == 'Word by Word (IndoPak Nastaleeq)':
        with open('indopak-nastaleeq.json', 'r', encoding='utf-8') as f:
            word_text_data = json.load(f)
    elif arabic_display_mode == 'Imlaei Script':
        with open('imlaei-script-ayah-by-ayah.json', 'r', encoding='utf-8') as f:
            imlaei_data = json.load(f)
    
    # Display ayahs
    for i, ayah in enumerate(arabic_ayahs):
        st.markdown(f"**Ayah {ayah['numberInSurah']}**")
        
        # Audio player
        if ayah.get('audio'):
            st.audio(ayah['audio'])
        
        # Display Arabic text based on mode
        if arabic_display_mode == 'Word Images (Calligraphy)':
            # Display word-by-word calligraphy images
            word_num = 1
            images_html = '<div style="text-align: right; direction: rtl;">'
            while True:
                word_key = f"{selected_surah_num}:{ayah['numberInSurah']}:{word_num}"
                if word_key in word_images_data:
                    img_url = word_images_data[word_key]['text']
                    images_html += f'<img src="{img_url}" style="height: {arabic_font_size * 2}px; margin: 2px;" />'
                    word_num += 1
                else:
                    break
            images_html += '</div>'
            st.markdown(images_html, unsafe_allow_html=True)
        elif arabic_display_mode == 'Tajweed Images (Colored)':
            # Display word-by-word Tajweed images
            word_num = 1
            images_html = '<div style="text-align: right; direction: rtl;">'
            while True:
                word_key = f"{selected_surah_num}:{ayah['numberInSurah']}:{word_num}"
                if word_key in tajweed_images_data:
                    img_url = tajweed_images_data[word_key]['text']
                    images_html += f'<img src="{img_url}" style="height: {arabic_font_size * 2}px; margin: 2px;" />'
                    word_num += 1
                else:
                    break
            images_html += '</div>'
            st.markdown(images_html, unsafe_allow_html=True)
        elif arabic_display_mode in ['Word by Word (QPC Nastaleeq)', 'Word by Word (IndoPak Nastaleeq)']:
            # Display word-by-word Nastaleeq text
            word_num = 1
            words_html = '<div style="text-align: right; direction: rtl;">'
            while True:
                word_key = f"{selected_surah_num}:{ayah['numberInSurah']}:{word_num}"
                if word_key in word_text_data:
                    word_text = word_text_data[word_key]['text']
                    words_html += f'<span style="font-family: \"{arabic_font}\", serif; font-size: {arabic_font_size}px; margin: 0 5px;">{word_text}</span>'
                    word_num += 1
                else:
                    break
            words_html += '</div>'
            st.markdown(words_html, unsafe_allow_html=True)
        elif arabic_display_mode == 'Imlaei Script':
            # Display Imlaei script (modern Arabic)
            ayah_key = f"{selected_surah_num}:{ayah['numberInSurah']}"
            if ayah_key in imlaei_data:
                imlaei_text = imlaei_data[ayah_key]['text']
                st.markdown(f"<p style='text-align: right; font-family: \"{arabic_font}\", serif; font-size: {arabic_font_size}px;'>{imlaei_text}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='text-align: right; font-family: \"{arabic_font}\", serif; font-size: {arabic_font_size}px;'>{ayah['text']}</p>", unsafe_allow_html=True)
        else:
            # Standard Uthmani text display
            st.markdown(f"<p style='text-align: right; font-family: \"{arabic_font}\", serif; font-size: {arabic_font_size}px;'>{ayah['text']}</p>", unsafe_allow_html=True)
        
        if show_translation and translation_ayahs[i]:
            st.markdown(f"<p style='font-family: \"{urdu_font}\", serif; font-size: {urdu_font_size}px;'>{translation_ayahs[i]['text']}</p>", unsafe_allow_html=True)
        
        if show_tafsir:
            tafsir_key = f"{selected_surah_num}:{ayah['numberInSurah']}"
            if tafsir_key in tafsir_data:
                st.markdown(f"**📖 Tafsir ({tafsir_choice}):**")
                # Get tafsir text - handle both dict and string formats
                tafsir_value = tafsir_data[tafsir_key]
                if isinstance(tafsir_value, dict):
                    tafsir_text = tafsir_value.get('t') or tafsir_value.get('text', '')
                else:
                    tafsir_text = tafsir_value
                st.markdown(f"<p style='font-family: \"{urdu_font}\", serif; font-size: {urdu_font_size}px; background-color: #f0f8ff; padding: 10px; border-radius: 5px;'>{tafsir_text}</p>", unsafe_allow_html=True)
        
        if show_matching_ayahs:
            ayah_key = f"{selected_surah_num}:{ayah['numberInSurah']}"
            if ayah_key in matching_data and matching_data[ayah_key]:
                st.markdown(f"**🔍 Matching Ayahs ({matching_choice}):**")
                st.markdown(f"<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;'>", unsafe_allow_html=True)
                
                for match in matching_data[ayah_key][:3]:  # Show top 3 matches
                    matched_ayah = match.get('matched_ayah', '')
                    score = match.get('score', 0)
                    matched_words_count = match.get('matched_words_count', 0)
                    
                    if matched_ayah:
                        # Parse surah:ayah format
                        try:
                            surah_num, ayah_num = matched_ayah.split(':')
                            surah_name = next((s['name'] for s in surah_list if s['number'] == int(surah_num)), f'Surah {surah_num}')
                            st.markdown(f"• **{surah_name} ({surah_num}:{ayah_num})** - Score: {score}%, Words: {matched_words_count}", unsafe_allow_html=True)
                        except:
                            st.markdown(f"• **{matched_ayah}** - Score: {score}%, Words: {matched_words_count}", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
    

elif page == 'FAQ':
    st.title('❓ اکثر پوچھے جانے والے سوالات - FAQ')
    st.markdown("""
    <div style='font-family: "Noto Nastaliq Urdu", serif; font-size: 18px; line-height: 2.5;'>
        <div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2>سوال: یہ ویب سائٹ کیسے استعمال کریں؟</h2>
            <p><strong>جواب:</strong> سائیڈبار سے سورہ منتخب کریں، اپنی پسند کی ترجمہ اور تفسیر کا انتخاب کریں، اور قرآن پڑھنا شروع کریں۔ آڈیو سننے کے لیے پلے بٹن دبائیں۔</p>
        </div>
        
        <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2>سوال: کیا یہ مفت ہے؟</h2>
            <p><strong>جواب:</strong> جی ہاں، یہ مکمل طور پر مفت ہے اور ہمیشہ رہے گا۔ کوئی چارجز، کوئی اکاؤنٹ، کوئی ایڈورٹائزنگ نہیں۔</p>
        </div>
        
        <div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2>سوال: آڈیو کیسے چلائیں؟</h2>
            <p><strong>جواب:</strong> ہر آیت کے ساتھ آڈیو پلیئر موجود ہے۔ پلے بٹن دبائیں اور مختلف قاریوں میں سے انتخاب کریں۔</p>
        </div>
        
        <div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2>سوال: فونٹ کیسے تبدیل کریں؟</h2>
            <p><strong>جواب:</strong> سائیڈبار میں Font Settings سے عربی اور اردو فونٹ تبدیل کر سکتے ہیں۔ فونٹ سائز بھی ایڈجسٹ کر سکتے ہیں۔</p>
        </div>
        
        <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2>سوال: موبائل پر کیسے استعمال کریں؟</h2>
            <p><strong>جواب:</strong> یہ ویب سائٹ مکمل طور پر موبائل فرینڈلی ہے۔ صرف اپنے موبائل براؤزر میں کھولیں اور استعمال کریں۔</p>
        </div>
        
        <div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2>سوال: کتنے تراجم اور تفاسیر موجود ہیں؟</h2>
            <p><strong>جواب:</strong> 10+ اردو اور انگریزی تراجم اور 5 مشہور تفاسیر موجود ہیں۔</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    

elif page == 'Credits':
    st.title('🌟 تشکرات - Credits')
    st.markdown("""
    <div style='font-family: "Noto Nastaliq Urdu", serif; font-size: 18px; line-height: 2.5;'>
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 20px;'>
            <h2 style='color: white;'>ڈیٹا کے ذرائع</h2>
            <ul style='font-size: 18px;'>
                <li><strong>عربی متن:</strong> Tanzil.net - عثمانی رسم الخط</li>
                <li><strong>آڈیو:</strong> EveryAyah.com - مختلف قاریوں کی تلاوت</li>
                <li><strong>خطاطی:</strong> QUL (Tarteel.ai) - خوبصورت خطاطی کی تصاویر</li>
                <li><strong>ترجمے:</strong> مستند علماء کے تراجم</li>
                <li><strong>تفاسیر:</strong> مشہور مفسرین کی تفاسیر</li>
            </ul>
        </div>
        
        <div style='background-color: #f0f8ff; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h2>خاص شکریہ</h2>
            <p style='font-size: 18px;'>
            • تمام علماء اور مترجمین جن کا کام یہاں شامل ہے<br>
            • <strong>Tanzil.net</strong> ٹیم<br>
            • <strong>EveryAyah.com</strong><br>
            • <strong>Tarteel.ai (QUL)</strong><br>
            • <strong>AlQuran.cloud</strong><br>
            • تمام اوپن سورس کنٹریبیوٹرز
            </p>
        </div>
        
        <div style='background-color: #fff3cd; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h2>ٹیکنالوجی</h2>
            <p style='font-size: 18px;'>
            • <strong>Streamlit</strong> - Python Framework<br>
            • <strong>HTML, CSS, JavaScript</strong><br>
            • <strong>Google Fonts</strong><br>
            • <strong>SQLite Database</strong><br>
            • <strong>Multiple APIs</strong>
            </p>
        </div>
        
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 15px; color: white; text-align: center;'>
            <h2 style='color: white; font-size: 28px;'>جزاک اللہ خیراً</h2>
            <p style='color: white; font-size: 20px; margin-top: 15px;'>
                اللہ تعالیٰ سب کی محنت قبول فرمائے اور اس کام کو امت مسلمہ کے لیے نفع بخش بنائے۔ آمین
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    

elif page == 'Privacy Policy':
    st.title('🔒 رازداری کی پالیسی - Privacy Policy')
    st.markdown("""
    <div style='font-family: "Noto Nastaliq Urdu", serif; font-size: 18px; line-height: 2.5;'>
        <div style='background-color: #e8f5e9; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h2>آپ کی رازداری ہماری ترجیح ہے</h2>
            <p style='font-size: 20px;'>
                ہم آپ کی رازداری کو انتہائی سنجیدگی سے لیتے ہیں اور کسی بھی قسم کی ذاتی معلومات جمع نہیں کرتے۔
            </p>
        </div>
        
        <div style='background-color: #ffebee; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h2>❌ ہم کیا جمع نہیں کرتے</h2>
            <ul style='font-size: 18px;'>
                <li>کوئی ذاتی معلومات جمع نہیں کرتے</li>
                <li>کوئی کوکیز یا ٹریکنگ نہیں</li>
                <li>کوئی اکاؤنٹ یا لاگ ان کی ضرورت نہیں</li>
                <li>کوئی ایڈورٹائزنگ نہیں</li>
                <li>ڈیٹا کو شیئر نہیں کرتے</li>
                <li>کوئی analytics نہیں</li>
            </ul>
        </div>
        
        <div style='background-color: #e3f2fd; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h2>✅ ہم کیا کرتے ہیں</h2>
            <ul style='font-size: 18px;'>
                <li>قرآنی مواد تک مفت رسائی فراہم کرتے ہیں</li>
                <li>پبلک APIs استعمال کرتے ہیں</li>
                <li>تمام ڈیٹا لوکل طور پر محفوظ ہے</li>
                <li>آپ کی ترجیحات صرف آپ کے براؤزر میں محفوظ ہوتی ہیں</li>
                <li>کھلے ذرائع (Open Source) استعمال کرتے ہیں</li>
            </ul>
        </div>
        
        <div style='background-color: #fff3e0; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h2>🌐 بیرونی خدمات</h2>
            <p style='font-size: 18px;'>
                <strong>ہم استعمال کرتے ہیں:</strong><br><br>
                • <strong>آڈیو:</strong> EveryAyah.com (مفت عوامی سروس)<br>
                • <strong>فونٹس:</strong> Google Fonts CDN<br>
                • <strong>تصاویر:</strong> QUL Tarteel.ai (عوامی CDN)<br><br>
                یہ خدمات کی اپنی رازداری کی پالیسیاں ہو سکتی ہیں۔
            </p>
        </div>
        
        <div style='background-color: #e8f5e9; padding: 30px; border-radius: 15px; border-left: 5px solid #4caf50;'>
            <h2>✔️ یقین دہانی</h2>
            <p style='font-size: 20px;'>
                <strong>یہ پلیٹ فارم مکمل طور پر مفت ہے اور آپ کی رازداری کا مکمل احترام کرتا ہے۔</strong><br><br>
                کوئی چھپے ہوئے چارجز نہیں، کوئی ڈیٹا کی فروخت نہیں، صرف خالص نیت سے امت مسلمہ کی خدمت۔
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
