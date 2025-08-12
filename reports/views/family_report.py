from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reports.forms import FamilyReportForm
from congregation.models import Family, Member
import requests
import base64

@login_required
def family_report_form(request):
    if request.method == 'POST':
        form = FamilyReportForm(request.POST)
        if form.is_valid():
            church = form.cleaned_data['church']
            
            # Get all families in the church
            families = Family.objects.filter(
                area__church=church
            ).order_by('area__area_id', 'family_id')
            
            # Prepare PDF data
            pdf_data = {
                "security": {
                    "key": "your_random_secret_key_here"
                },
                "page": {
                    "orientation": "P",  # Portrait orientation
                    "format": "A4",
                    "margin_left": 5,   # 0.5 cm margins
                    "margin_right": 5,
                    "margin_top": 5,
                    "margin_bottom": 5
                },
                "content": [
                    # Draw border lines around the page with exact coordinates
                    {
                        "type": "drawLine",
                        "x1": 10,
                        "y1": 10,
                        "x2": 287,
                        "y2": 10,
                        "width": 0.12,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 287,
                        "y1": 10,
                        "x2": 287,
                        "y2": 200,
                        "width": 0.12,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 10,
                        "y1": 10,
                        "x2": 10,
                        "y2": 200,
                        "width": 0.12,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 10,
                        "y1": 200,
                        "x2": 287,
                        "y2": 200,
                        "width": 0.12,
                        "color": "#000000"
                    },
                    # Page number in top right corner
                    {
                        "type": "writebook",
                        "text": "Page 1",
                        "rotate": 0,
                        "top": 7,
                        "left": 170,
                        "height": 5,
                        "width": 30,
                        "fontSize": 8,
                        "align": "right",
                        "fontFamily": "Times New Roman",
                        "lineheight": 5,
                        "bold": True,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    # Church name header
                    {
                        "type": "writebook",
                        "text": f"{church.church_name} - FAMILY REPORT",
                        "rotate": 0,
                        "top": 7,
                        "left": 5,
                        "height": 8,
                        "width": 200,
                        "fontSize": 14,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 8,
                        "bold": True,
                        "border": "0px solid #000",
                        "padding": 0
                    }
                ]
            }
            
            current_y = 18  # Starting Y position after header
            
            for family in families:
                # Get members of the family
                members = Member.objects.filter(family=family).order_by('member_id')
                
                # Add line before family section
                pdf_data["content"].append({
                    "type": "drawLine",
                    "x1": 5,
                    "y1": current_y,
                    "x2": 205,
                    "y2": current_y,
                    "width": 0.1,
                    "color": "#000000"
                })
                
                current_y += 2  # Space after line
                
                # Family header
                pdf_data["content"].extend([
                    {
                        "type": "writebook",
                        "text": f"Family No : {family.family_id}",
                        "rotate": 0,
                        "top": current_y,
                        "left": 7,
                        "height": 5,
                        "width": 50,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 5,
                        "bold": True,  # Bold family header
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": f"Area : {family.area.area_name}",
                        "rotate": 0,
                        "top": current_y,
                        "left": 57,
                        "height": 5,
                        "width": 50,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 5,
                        "bold": True,  # Bold area header
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": f"Fellowship : {family.fellowship.fellowship_name}",
                        "rotate": 0,
                        "top": current_y,
                        "left": 107,
                        "height": 5,
                        "width": 50,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 5,
                        "bold": True,  # Bold fellowship header
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": f"Mobile : {family.mobile}",
                        "rotate": 0,
                        "top": current_y,
                        "left": 157,
                        "height": 5,
                        "width": 50,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 5,
                        "bold": True,  # Bold mobile header
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    # Address
                    {
                        "type": "writebook",
                        "text": f"Address: {family.address}",
                        "rotate": 0,
                        "top": current_y + 5,
                        "left": 7,
                        "height": 5,
                        "width": 195,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "lineheight": 5,
                        "bold": True,  # Bold address header
                        "border": "0px solid #000",
                        "padding": 0
                    }
                ])
                
                # Draw table header lines
                current_y += 11
                pdf_data["content"].extend([
                    # Horizontal line below address
                    {
                        "type": "drawLine",
                        "x1": 5,
                        "y1": current_y,
                        "x2": 205,
                        "y2": current_y,
                        "width": 0.1,
                        "color": "#000000"
                    },
                    # Table headers
                    {
                        "type": "writebook",
                        "text": "M.NO",
                        "rotate": 0,
                        "top": current_y + 1,
                        "left": 7,
                        "height": 5,
                        "width": 15,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "bold": True,
                        "lineheight": 5,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": "Names",
                        "rotate": 0,
                        "top": current_y + 1,
                        "left": 22,
                        "height": 5,
                        "width": 50,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "bold": True,
                        "lineheight": 5,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": "Age",
                        "rotate": 0,
                        "top": current_y + 1,
                        "left": 72,
                        "height": 5,
                        "width": 15,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "bold": True,
                        "lineheight": 5,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": "Relationship",
                        "rotate": 0,
                        "top": current_y + 1,
                        "left": 87,
                        "height": 5,
                        "width": 30,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "bold": True,
                        "lineheight": 5,
                        "border": "0px solid #000",
                        "padding": 0
                    },
                    {
                        "type": "writebook",
                        "text": "Working place - Working Area",
                        "rotate": 0,
                        "top": current_y + 1,
                        "left": 117,
                        "height": 5,
                        "width": 85,
                        "fontSize": 10,
                        "align": "left",
                        "fontFamily": "Times New Roman",
                        "bold": True,
                        "lineheight": 5,
                        "border": "0px solid #000",
                        "padding": 0
                    }
                ])
                
                # Add line after column headers
                current_y += 6
                pdf_data["content"].append({
                    "type": "drawLine",
                    "x1": 5,
                    "y1": current_y,
                    "x2": 205,
                    "y2": current_y,
                    "width": 0.1,
                    "color": "#000000"
                })
                
                # Draw vertical lines for table
                pdf_data["content"].extend([
                    {
                        "type": "drawLine",
                        "x1": 5,  # Left border of table
                        "y1": current_y - 6,  # Start from header line
                        "x2": 5,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.1,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 20,  # After M.NO
                        "y1": current_y - 6,  # Start from header line
                        "x2": 20,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.1,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 70,  # After Names
                        "y1": current_y - 6,  # Start from header line
                        "x2": 70,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.1,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 85,  # After Age
                        "y1": current_y - 6,  # Start from header line
                        "x2": 85,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.1,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 115,  # After Relationship
                        "y1": current_y - 6,  # Start from header line
                        "x2": 115,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.1,
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 205,  # Right border of table
                        "y1": current_y - 6,  # Start from header line
                        "x2": 205,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.1,
                        "color": "#000000"
                    }
                ])
                
                # Add member rows
                current_y += 2
                for i, member in enumerate(members):
                    pdf_data["content"].extend([
                        {
                            "type": "writebook",
                            "text": str(member.member_id).split('-')[-1],
                            "rotate": 0,
                            "top": current_y,
                            "left": 7,
                            "height": 5,
                            "width": 13,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": f"{member.respect.name} {member.initial} {member.name}",
                            "rotate": 0,
                            "top": current_y,
                            "left": 22,
                            "height": 5,
                            "width": 48,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": str(member.age if member.age else ''),
                            "rotate": 0,
                            "top": current_y,
                            "left": 72,
                            "height": 5,
                            "width": 13,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": member.relation.name,
                            "rotate": 0,
                            "top": current_y,
                            "left": 87,
                            "height": 5,
                            "width": 28,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": f"{member.working} - {member.working_place}" if member.working else "",
                            "rotate": 0,
                            "top": current_y,
                            "left": 117,
                            "height": 5,
                            "width": 85,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "border": "0px solid #000",
                            "padding": 0
                        }
                    ])
                    
                    # Add horizontal line after each member except the last one
                    if i < len(members) - 1:
                        row_y = current_y + 8
                        pdf_data["content"].append({
                            "type": "drawLine",
                            "x1": 5,
                            "y1": row_y,
                            "x2": 205,
                            "y2": row_y,
                            "width": 0.1,
                            "color": "#000000"
                        })
                    
                    current_y += 8
                
                # Add bottom line for members table
                pdf_data["content"].append({
                    "type": "drawLine",
                    "x1": 5,
                    "y1": current_y,
                    "x2": 205,
                    "y2": current_y,
                    "width": 0.1,
                    "color": "#000000"
                })
                
                current_y += 2  # Space after line
                
                # Add prayer points after members table
                if family.prayer_points:
                    pdf_data["content"].extend([
                        {
                            "type": "writebook",
                            "text": "Prayer Points:",
                            "rotate": 0,
                            "top": current_y,
                            "left": 7,
                            "height": 5,
                            "width": 30,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "bold": True,
                            "lineheight": 5,
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": family.prayer_points,
                            "rotate": 0,
                            "top": current_y,
                            "left": 37,
                            "height": 5,
                            "width": 165,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "border": "0px solid #000",
                            "padding": 0
                        }
                    ])
                    current_y += 7  # Space after prayer points
                
                # No extra space between families
                
                # Add page break if needed
                if current_y > 287:  # A4 height minus margins
                    current_y = 18
                    pdf_data["content"].extend([
                        {
                            "type": "addPage",
                            "format": "A4",
                            "orientation": "P"
                        },
                        # Draw border lines around the new page with exact coordinates
                        {
                            "type": "drawLine",
                            "x1": 10,
                            "y1": 10,
                            "x2": 287,
                            "y2": 10,
                            "width": 0.5,
                            "color": "#000000"
                        },
                        {
                            "type": "drawLine",
                            "x1": 287,
                            "y1": 10,
                            "x2": 287,
                            "y2": 200,
                            "width": 0.5,
                            "color": "#000000"
                        },
                        {
                            "type": "drawLine",
                            "x1": 10,
                            "y1": 10,
                            "x2": 10,
                            "y2": 200,
                            "width": 0.5,
                            "color": "#000000"
                        },
                        {
                            "type": "drawLine",
                            "x1": 10,
                            "y1": 200,
                            "x2": 287,
                            "y2": 200,
                            "width": 0.5,
                            "color": "#000000"
                        },
                        # Page number in top right corner
                        {
                            "type": "writebook",
                            "text": f"Page {len(pdf_data['content']) // 100 + 2}",  # Estimate page number
                            "rotate": 0,
                            "top": 7,
                            "left": 170,
                            "height": 5,
                            "width": 30,
                            "fontSize": 8,
                            "align": "right",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "bold": True,
                            "border": "0px solid #000",
                            "padding": 0
                        }
                    ])
            
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
                        response['Content-Disposition'] = f'attachment; filename="family_report_{church.short_name}.pdf"'
                    else:  # action == 'view'
                        response['Content-Disposition'] = f'inline; filename="family_report_{church.short_name}.pdf"'
                    
                    return response
                else:
                    form.add_error(None, f"Error generating PDF: {response.text}")
            except Exception as e:
                form.add_error(None, f"An error occurred: {str(e)}")
    else:
        form = FamilyReportForm()
    
    context = {
        'title': 'Family Report',
        'form': form
    }
    return render(request, 'reports/family_report_form.html', context)