from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "school_accounting.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stage TEXT NOT NULL,
            category TEXT NOT NULL,
            total_amount REAL NOT NULL,
            paid_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Active',
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

TRANSLATIONS = {
    'ar': {
        'title': 'بوابة الحسابات المدرسية',
        'search_placeholder': 'ابحث بالاسم أو الرقم...',
        'all_stages': 'جميع المراحل الدراسية',
        'stage_k': 'الروضة',
        'stage_b': 'المرحلة الأساسية',
        'stage_p': 'المرحلة الإعدادية',
        'fees': 'أقساط دراسية',
        'expenses': 'مصروفات تشغيلية',
        'add_new': '+ إضافة سجل حساب جديد',
        'name': 'اسم الطالب / الحساب',
        'stage': 'المرحلة',
        'category': 'التصنيف',
        'total': 'المبلغ الكلي',
        'paid': 'الواصل',
        'remaining': 'المتبقي',
        'status': 'الحالة',
        'save': 'حفظ البيانات',
        'cancel': 'إلغاء'
    },
    'ku': {
        'title': 'دەروازەی ژمێریاری قوتابخانە',
        'search_placeholder': 'گەڕان بە ناو یان ژمارە...',
        'all_stages': 'هەموو قۆناغەکانی خوێندن',
        'stage_k': 'باخچەی ساوایان',
        'stage_b': 'قۆناغی بنەڕەتی',
        'stage_p': 'قۆناغی ئامادەیی',
        'fees': 'قستەکانی خوێندن',
        'expenses': 'خەرجییەکانی کارکردن',
        'add_new': '+ زیادکردنی تۆماری نوێ',
        'name': 'ناوی قوتابی / هەژمار',
        'stage': 'قۆناغ',
        'category': 'پۆلێن',
        'total': 'کۆی گشتی پارە',
        'paid': 'دراوە',
        'remaining': 'ماوەوە',
        'status': 'دۆخ',
        'save': 'پاشەکەوت کردن',
        'cancel': 'پاشگەزبوونەوە'
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    lang = request.args.get('lang', 'ar')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['ar'])
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        stage = request.form['stage']
        category = request.form['category']
        total_amount = float(request.form['total_amount'])
        paid_amount = float(request.form['paid_amount'])
        status = request.form['status']
        date = request.form['date']
        
        cursor.execute('''
            INSERT INTO accounts (name, stage, category, total_amount, paid_amount, status, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, stage, category, total_amount, paid_amount, status, date))
        conn.commit()
        return redirect(url_for('index', lang=lang))
    
    search_query = request.args.get('q', '')
    stage_filter = request.args.get('stage', 'all')
    
    query = "SELECT * FROM accounts WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (name LIKE ? OR id LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    if stage_filter != 'all':
        query += " AND stage = ?"
        params.append(stage_filter)
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', t=t, lang=lang, records=records, search_query=search_query, stage_filter=stage_filter)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)