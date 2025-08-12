from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from congregation.models import Church, Family, Member
import requests
import base64
from datetime import datetime, timedelta
import calendar

@login_required
def generate_wedding_report(request):
    if request.method == 'POST':
        church_id = request.POST.get('church')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        
        try:
            church = Church.objects.get(id=church_id)
            
            # Parse dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Get all members in the church with wedding anniversaries in the selected date range
            # We need to check day and month, ignoring year
            wedding_members = []
            all_members = Member.objects.filter(family__area__church=church)
            
            for member in all_members:
                if member.dom:  # date of marriage
                    # Create a date object for this year's anniversary
                    current_year = datetime.now().year
                    anniversary_this_year = datetime(current_year, member.dom.month, member.dom.day).date()
                    
                    # Check if anniversary falls within the date range
                    # We only care about month and day, not the year
                    start_month_day = (start_date.month, start_date.day)
                    end_month_day = (end_date.month, end_date.day)
                    anniversary_month_day = (member.dom.month, member.dom.day)
                    
                    # Handle date ranges that span across years (e.g., Dec 15 to Jan 15)
                    if start_month_day <= end_month_day:
                        # Normal case: date range within same year
                        if start_month_day <= anniversary_month_day <= end_month_day:
                            wedding_members.append(member)
                    else:
                        # Date range spans across years
                        if anniversary_month_day >= start_month_day or anniversary_month_day <= end_month_day:
                            wedding_members.append(member)
            
            # Sort by anniversary (month and day)
            wedding_members.sort(key=lambda m: (m.dom.month, m.dom.day))
            
            # Group members by family
            families_with_anniversaries = {}
            for member in wedding_members:
                if member.family.id not in families_with_anniversaries:
                    families_with_anniversaries[member.family.id] = {
                        'family': member.family,
                        'members': [],
                        'celebrants': []
                    }
                families_with_anniversaries[member.family.id]['members'].append(member)
                families_with_anniversaries[member.family.id]['celebrants'].append(member)
            
            # For each family with wedding celebrants, get all members
            for family_id, data in families_with_anniversaries.items():
                all_family_members = Member.objects.filter(family=data['family']).order_by('member_id')
                data['members'] = all_family_members
            
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
                    # Report header
                    {
                        "type": "writebook",
                        "text": f"{church.church_name} - WEDDING ANNIVERSARY CELEBRATION REPORT",
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
                    },
                    # Date range header
                    {
                        "type": "writebook",
                        "text": f"Date Range: {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}",
                        "rotate": 0,
                        "top": 15,
                        "left": 5,
                        "height": 6,
                        "width": 200,
                        "fontSize": 12,
                        "align": "center",
                        "fontFamily": "Times New Roman",
                        "lineheight": 6,
                        "bold": True,
                        "border": "0px solid #000",
                        "padding": 0
                    }
                ]
            }
            
            current_y = 25  # Starting Y position after header
            
            for family_id, data in families_with_anniversaries.items():
                family = data['family']
                members = data['members']
                celebrants = data['celebrants']
                
                # Add line before family section
                pdf_data["content"].append({
                    "type": "drawLine",
                    "x1": 5,
                    "y1": current_y,
                    "x2": 205,
                    "y2": current_y,
                    "width": 0.3,  # Thicker line for outer border
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
                        "width": 0.3,  # Thicker line for outer border
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
                        "text": "Working place",
                        "rotate": 0,
                        "top": current_y + 1,
                        "left": 117,
                        "height": 5,
                        "width": 40,
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
                        "text": "Anniversary Date",
                        "rotate": 0,
                        "top": current_y + 1,
                        "left": 157,
                        "height": 5,
                        "width": 40,
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
                    "width": 0.2,  # Medium thickness for inner lines
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
                        "width": 0.3,  # Thicker line for outer border
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 20,  # After M.NO
                        "y1": current_y - 6,  # Start from header line
                        "x2": 20,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.2,  # Medium thickness for inner lines
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 70,  # After Names
                        "y1": current_y - 6,  # Start from header line
                        "x2": 70,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.2,  # Medium thickness for inner lines
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 85,  # After Age
                        "y1": current_y - 6,  # Start from header line
                        "x2": 85,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.2,  # Medium thickness for inner lines
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 115,  # After Relationship
                        "y1": current_y - 6,  # Start from header line
                        "x2": 115,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.2,  # Medium thickness for inner lines
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 155,  # After Working place
                        "y1": current_y - 6,  # Start from header line
                        "x2": 155,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.2,  # Medium thickness for inner lines
                        "color": "#000000"
                    },
                    {
                        "type": "drawLine",
                        "x1": 205,  # Right border of table
                        "y1": current_y - 6,  # Start from header line
                        "x2": 205,
                        "y2": current_y + (len(members) * 8) + 2,
                        "width": 0.3,  # Thicker line for outer border
                        "color": "#000000"
                    }
                ])
                
                # Add member rows
                current_y += 2
                for i, member in enumerate(members):
                    # Check if this member is a wedding celebrant
                    is_celebrant = member in celebrants
                    anniversary_text = ""
                    if member.dom:
                        # Calculate years of marriage
                        years_married = datetime.now().year - member.dom.year
                        anniversary_text = f"{member.dom.strftime('%d-%m-%Y')} ({years_married} years)"
                    
                    # Set text color for celebrants
                    text_color = "#B22222" if is_celebrant else "#000000"  # Dark red for celebrants
                    
                    # Add celebrant indicator
                    celebrant_indicator = "★ " if is_celebrant else ""
                    
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
                            "bold": is_celebrant,  # Bold if celebrant
                            "color": text_color,  # Color for celebrant
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": f"{celebrant_indicator}{member.respect.name} {member.initial} {member.name}",
                            "rotate": 0,
                            "top": current_y,
                            "left": 22,
                            "height": 5,
                            "width": 48,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "bold": is_celebrant,  # Bold if celebrant
                            "color": text_color,  # Color for celebrant
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
                            "bold": is_celebrant,  # Bold if celebrant
                            "color": text_color,  # Color for celebrant
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
                            "bold": is_celebrant,  # Bold if celebrant
                            "color": text_color,  # Color for celebrant
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": f"{member.working}" if member.working else "",
                            "rotate": 0,
                            "top": current_y,
                            "left": 117,
                            "height": 5,
                            "width": 38,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "bold": is_celebrant,  # Bold if celebrant
                            "color": text_color,  # Color for celebrant
                            "border": "0px solid #000",
                            "padding": 0
                        },
                        {
                            "type": "writebook",
                            "text": anniversary_text,
                            "rotate": 0,
                            "top": current_y,
                            "left": 157,
                            "height": 5,
                            "width": 48,
                            "fontSize": 10,
                            "align": "left",
                            "fontFamily": "Times New Roman",
                            "lineheight": 5,
                            "bold": is_celebrant,  # Bold if celebrant
                            "color": text_color,  # Color for celebrant
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
                            "width": 0.2,  # Medium thickness for inner lines
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
                    "width": 0.3,  # Thicker line for outer border
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
                        response['Content-Disposition'] = f'attachment; filename="wedding_report_{church.short_name}_{start_date.strftime("%d%m%Y")}_to_{end_date.strftime("%d%m%Y")}.pdf"'
                    else:  # action == 'view'
                        response['Content-Disposition'] = f'inline; filename="wedding_report_{church.short_name}_{start_date.strftime("%d%m%Y")}_to_{end_date.strftime("%d%m%Y")}.pdf"'
                    
                    return response
                else:
                    return JsonResponse({'error': f"Error generating PDF: {response.text}"}, status=400)
            except Exception as e:
                return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)
        except Church.DoesNotExist:
            return JsonResponse({'error': 'Church not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def get_churches_for_wedding(request):
    """API endpoint to get churches for the wedding report form"""
    churches = Church.objects.all().order_by('church_name')
    data = [{'id': church.id, 'name': church.church_name} for church in churches]
    return JsonResponse(data, safe=False) 