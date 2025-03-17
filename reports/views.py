from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import BaptismRecordForm
import requests
import base64
from datetime import datetime

# Create your views here.

@login_required
def essentials(request):
    context = {
        'title': 'Reports Essentials',
        'subtitle': 'Generate church reports in Tamil'
    }
    return render(request, 'reports/essentials.html', context)

@login_required
def baptism_record_form(request):
    if request.method == 'POST':
        form = BaptismRecordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Format dates
            baptism_date = data['baptism_date'].strftime('%d-%m-%Y')
            birth_date = data['birth_date'].strftime('%d-%m-%Y')
            cert_date = data['certification_date'].strftime('%d-%m-%Y')
            
            # Determine font settings based on Tamil checkboxes
            name_font = "uniilasundaram07" if data.get('name_is_tamil', False) else "Times New Roman"
            name_font_size = 14 if data.get('name_is_tamil', False) else 12
            
            gender_font = "uniilasundaram07" if data.get('gender_is_tamil', False) else "Times New Roman"
            gender_font_size = 14 if data.get('gender_is_tamil', False) else 12
            
            occupation_font = "uniilasundaram07" if data.get('occupation_is_tamil', False) else "Times New Roman"
            occupation_font_size = 14 if data.get('occupation_is_tamil', False) else 12
            
            parents_font = "uniilasundaram07" if data.get('parents_is_tamil', False) else "Times New Roman"
            parents_font_size = 14 if data.get('parents_is_tamil', False) else 12
            
            godparents_font = "uniilasundaram07" if data.get('godparents_is_tamil', False) else "Times New Roman"
            godparents_font_size = 14 if data.get('godparents_is_tamil', False) else 12
            
            church_font = "uniilasundaram07" if data.get('church_is_tamil', False) else "Times New Roman"
            church_font_size = 14 if data.get('church_is_tamil', False) else 12
            
            minister_font = "uniilasundaram07" if data.get('minister_is_tamil', False) else "Times New Roman"
            minister_font_size = 14 if data.get('minister_is_tamil', False) else 12
            
            # Prepare PDF generation data
            pdf_data = {
                "security": {
                    "key": "your_random_secret_key_here"  # Replace with actual key
                },
                "page": {
                    "orientation": "L",
                    "format": "LEGAL",
                    "margin_left": 20,
                    "margin_right": 20,
                    "margin_top": 20,
                    "margin_bottom": 20
                },
                "content": [
                    {
                        "type": "addBg",
                        "path": "https://print.rexmi.in/img/infant.png",
                        "opa": 1.0
                    },
                    {
                        "type": "writebook",
                        "text": data['record_number'],
                        "rotate": -90,
                        "top": 89,
                        "left": 13,
                        "height": 16,
                        "width": 80,
                        "fontSize": 12,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 16,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": baptism_date,
                        "rotate": -90,
                        "top": 89,
                        "left": 29,
                        "height": 26,
                        "width": 79,
                        "fontSize": 12,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 26,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": birth_date,
                        "rotate": -90,
                        "top": 89,
                        "left": 55,
                        "height": 21,
                        "width": 79,
                        "fontSize": 12,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 21,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['name'],
                        "rotate": -90,
                        "top": 89,
                        "left": 76,
                        "height": 40,
                        "width": 80,
                        "fontSize": name_font_size,
                        "align": "center",
                        "fontFamily": name_font,
                        "lineheight": 40,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['gender'],
                        "rotate": -90,
                        "top": 88,
                        "left": 116,
                        "height": 18,
                        "width": 80,
                        "fontSize": gender_font_size,
                        "align": "center",
                        "fontFamily": gender_font,
                        "lineheight": 18,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['occupation'],
                        "rotate": -90,
                        "top": 89,
                        "left": 196,
                        "height": 34,
                        "width": 79,
                        "fontSize": occupation_font_size,
                        "align": "center",
                        "fontFamily": occupation_font,
                        "lineheight": 34,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['father_name'],
                        "rotate": -90,
                        "top": 88,
                        "left": 134,
                        "height": 16,
                        "width": 80,
                        "fontSize": parents_font_size,
                        "align": "center",
                        "fontFamily": parents_font,
                        "lineheight": 16,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['mother_name'],
                        "rotate": -90,
                        "top": 89,
                        "left": 149,
                        "height": 16,
                        "width": 80,
                        "fontSize": parents_font_size,
                        "align": "center",
                        "fontFamily": parents_font,
                        "lineheight": 16,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['godparent1_name'],
                        "rotate": -90,
                        "top": 89,
                        "left": 230,
                        "height": 13,
                        "width": 79,
                        "fontSize": godparents_font_size,
                        "align": "center",
                        "fontFamily": godparents_font,
                        "lineheight": 13,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['godparent2_name'],
                        "rotate": -90,
                        "top": 89,
                        "left": 244,
                        "height": 13,
                        "width": 79,
                        "fontSize": godparents_font_size,
                        "align": "center",
                        "fontFamily": godparents_font,
                        "lineheight": 13,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['godparent3_name'],
                        "rotate": -90,
                        "top": 89,
                        "left": 258,
                        "height": 13,
                        "width": 79,
                        "fontSize": godparents_font_size,
                        "align": "center",
                        "fontFamily": godparents_font,
                        "lineheight": 13,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['church_name'],
                        "rotate": -90,
                        "top": 89,
                        "left": 271,
                        "height": 25,
                        "width": 80,
                        "fontSize": church_font_size,
                        "align": "center",
                        "fontFamily": church_font,
                        "lineheight": 25,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['church_location'],
                        "rotate": -90,
                        "top": 89,
                        "left": 165,
                        "height": 31,
                        "width": 79,
                        "fontSize": church_font_size,
                        "align": "center",
                        "fontFamily": church_font,
                        "lineheight": 31,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": f"{data['minister_title']} {data['minister_name']}",
                        "rotate": -90,
                        "top": 88,
                        "left": 310,
                        "height": 20,
                        "width": 80,
                        "fontSize": minister_font_size,
                        "align": "center",
                        "fontFamily": minister_font,
                        "lineheight": 20,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": f"I {data['certifying_minister']} hereby certify that the above is a true extract from the Register of Baptism kept at {data['church_location_cert']}",
                        "rotate": 0,
                        "top": 178,
                        "left": 37,
                        "height": 7,
                        "width": 245,
                        "fontSize": 12,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 7,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": cert_date,
                        "rotate": 0,
                        "top": 189,
                        "left": 32,
                        "height": 7,
                        "width": 48,
                        "fontSize": 12,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 7,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['church_location_cert'],
                        "rotate": 0,
                        "top": 195,
                        "left": 32,
                        "height": 8,
                        "width": 92,
                        "fontSize": 12,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 8,
                        "border": "0px solid #000",
                        "padding": 0
                    }
                ]
            }
            
            try:
                response = requests.post('https://print.rexmi.in/index.php', 
                                      json=pdf_data,
                                      headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    result = response.json()
                    pdf_content = base64.b64decode(result['pdf_content'])
                    
                    # Create response with PDF
                    response = HttpResponse(pdf_content, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="baptism_record_{data["record_number"]}.pdf"'
                    return response
                else:
                    form.add_error(None, f"Error generating PDF: {response.text}")
            except Exception as e:
                form.add_error(None, f"An error occurred: {str(e)}")
    else:
        form = BaptismRecordForm()
    
    context = {
        'title': 'Infant Baptism Record',
        'form': form
    }
    return render(request, 'reports/baptism_record_form.html', context)
