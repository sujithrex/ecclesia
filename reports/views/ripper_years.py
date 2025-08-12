from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reports.forms import RipperYearsForm
import requests
import base64
from datetime import datetime

@login_required
def ripper_years_form(request):
    if request.method == 'POST':
        form = RipperYearsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Format dates
            baptism_date = data['baptism_date'].strftime('%d-%m-%Y')
            cert_date = data['certification_date'].strftime('%d-%m-%Y')
            
            # Determine font settings based on Tamil checkboxes
            christian_name_font = "uniilasundaram07" if data.get('christian_name_is_tamil', False) else "Times New Roman"
            christian_name_font_size = 14 if data.get('christian_name_is_tamil', False) else 12
            
            former_name_font = "uniilasundaram07" if data.get('former_name_is_tamil', False) else "Times New Roman"
            former_name_font_size = 14 if data.get('former_name_is_tamil', False) else 12
            
            gender_font = "uniilasundaram07" if data.get('gender_is_tamil', False) else "Times New Roman"
            gender_font_size = 14 if data.get('gender_is_tamil', False) else 12
            
            abode_font = "uniilasundaram07" if data.get('abode_is_tamil', False) else "Times New Roman"
            abode_font_size = 14 if data.get('abode_is_tamil', False) else 12
            
            occupation_font = "uniilasundaram07" if data.get('occupation_is_tamil', False) else "Times New Roman"
            occupation_font_size = 14 if data.get('occupation_is_tamil', False) else 12
            
            parents_font = "uniilasundaram07" if data.get('parents_is_tamil', False) else "Times New Roman"
            parents_font_size = 14 if data.get('parents_is_tamil', False) else 12
            
            godparents_font = "uniilasundaram07" if data.get('godparents_is_tamil', False) else "Times New Roman"
            godparents_font_size = 14 if data.get('godparents_is_tamil', False) else 12
            
            baptism_location_font = "uniilasundaram07" if data.get('baptism_location_is_tamil', False) else "Times New Roman"
            baptism_location_font_size = 14 if data.get('baptism_location_is_tamil', False) else 12
            
            minister_font = "uniilasundaram07" if data.get('minister_is_tamil', False) else "Times New Roman"
            minister_font_size = 14 if data.get('minister_is_tamil', False) else 12
            
            # Prepare PDF generation data
            pdf_data = {
                "security": {
                    "key": "your_random_secret_key_here"  # Replace with actual key
                },
                "page": {
                    "orientation": "L",
                    "format": "Legal",
                    "margin_left": 36,
                    "margin_right": 36,
                    "margin_top": 36,
                    "margin_bottom": 36
                },
                "content": [
                    {
                        "type": "addBg",
                        "path": "https://print.rexmi.in/img/ripper_bap.png",
                        "opa": 1.0
                    },
                    {
                        "type": "writebook",
                        "text": data['record_number'],
                        "rotate": -90,
                        "top": 87,
                        "left": 13,
                        "height": 20,
                        "width": 76,
                        "fontSize": 12,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 20,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": baptism_date,
                        "rotate": -90,
                        "top": 86,
                        "left": 33,
                        "height": 27,
                        "width": 76,
                        "fontSize": 12,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 27,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['christian_name'],
                        "rotate": -90,
                        "top": 86,
                        "left": 60,
                        "height": 33,
                        "width": 76,
                        "fontSize": christian_name_font_size,
                        "align": "center",
                        "fontFamily": christian_name_font,
                        "lineheight": 33,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['former_name'],
                        "rotate": -90,
                        "top": 86,
                        "left": 93,
                        "height": 25,
                        "width": 76,
                        "fontSize": former_name_font_size,
                        "align": "center",
                        "fontFamily": former_name_font,
                        "lineheight": 25,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['gender'],
                        "rotate": -90,
                        "top": 87,
                        "left": 118,
                        "height": 20,
                        "width": 76,
                        "fontSize": gender_font_size,
                        "align": "center",
                        "fontFamily": gender_font,
                        "lineheight": 20,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['age'],
                        "rotate": -90,
                        "top": 86,
                        "left": 138,
                        "height": 20,
                        "width": 76,
                        "fontSize": 12,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 20,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['abode'],
                        "rotate": -90,
                        "top": 85,
                        "left": 158,
                        "height": 20,
                        "width": 76,
                        "fontSize": abode_font_size,
                        "align": "center",
                        "fontFamily": abode_font,
                        "lineheight": 20,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['occupation'],
                        "rotate": -90,
                        "top": 87,
                        "left": 178,
                        "height": 26,
                        "width": 76,
                        "fontSize": occupation_font_size,
                        "align": "center",
                        "fontFamily": occupation_font,
                        "lineheight": 26,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['father_name'],
                        "rotate": -90,
                        "top": 86,
                        "left": 204,
                        "height": 18,
                        "width": 76,
                        "fontSize": parents_font_size,
                        "align": "center",
                        "fontFamily": parents_font,
                        "lineheight": 18,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['mother_name'],
                        "rotate": -90,
                        "top": 86,
                        "left": 222,
                        "height": 16,
                        "width": 76,
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
                        "top": 86,
                        "left": 238,
                        "height": 14,
                        "width": 76,
                        "fontSize": godparents_font_size,
                        "align": "center",
                        "fontFamily": godparents_font,
                        "lineheight": 14,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['godparent2_name'],
                        "rotate": -90,
                        "top": 88,
                        "left": 252,
                        "height": 12,
                        "width": 75,
                        "fontSize": godparents_font_size,
                        "align": "center",
                        "fontFamily": godparents_font,
                        "lineheight": 12,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['godparent3_name'],
                        "rotate": -90,
                        "top": 86,
                        "left": 263,
                        "height": 11,
                        "width": 76,
                        "fontSize": godparents_font_size,
                        "align": "center",
                        "fontFamily": godparents_font,
                        "lineheight": 11,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": data['baptism_location'],
                        "rotate": -90,
                        "top": 86,
                        "left": 274,
                        "height": 31,
                        "width": 76,
                        "fontSize": baptism_location_font_size,
                        "align": "center",
                        "fontFamily": baptism_location_font,
                        "lineheight": 31,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": f"{data['minister_title']} {data['minister_name']}",
                        "rotate": -90,
                        "top": 86,
                        "left": 306,
                        "height": 38,
                        "width": 76,
                        "fontSize": minister_font_size,
                        "align": "center",
                        "fontFamily": minister_font,
                        "lineheight": 38,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": f"I {data['certifying_minister']} hereby certify that the above is a true extract from the Register of Baptism kept at {data['church_location_cert']}",
                        "rotate": 0,
                        "top": 169,
                        "left": 12,
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
                    
                    # Check if the user wants to view or download the PDF
                    action = request.POST.get('action', 'download')
                    if action == 'download':
                        response['Content-Disposition'] = f'attachment; filename="ripper_years_{data["record_number"]}.pdf"'
                    else:  # action == 'view'
                        response['Content-Disposition'] = f'inline; filename="ripper_years_{data["record_number"]}.pdf"'
                    
                    return response
                else:
                    form.add_error(None, f"Error generating PDF: {response.text}")
            except Exception as e:
                form.add_error(None, f"An error occurred: {str(e)}")
    else:
        form = RipperYearsForm()
    
    context = {
        'title': 'Ripper Years Record',
        'form': form
    }
    return render(request, 'reports/ripper_years_form.html', context) 