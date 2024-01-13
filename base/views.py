from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django. contrib import messages
from .models import senior_list, SMSMessage, osca_list
from .forms import register_form
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse
import csv

from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client

from django.contrib import messages
from django.utils import timezone

import json
import base64
import numpy as np
import cv2
import os
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import face_recognition
import dlib
from PIL import Image
from django.db.models import Count


from django.http import HttpResponseRedirect, FileResponse
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.db.models import Max, Min
from reportlab.platypus import Spacer
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image

def download_summary(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="senior_list_report.pdf"'

    seniors = senior_list.objects.all()

    Claimed_accounts = seniors.filter(is_claimed=True)

    Claimed_data = [['OSCA ID', 'Last Name','First Name', 'Claimed Date', 'Allowance Type', 'Allowance Amount']]

    claimed_count = seniors.filter(is_claimed=True).count()
    claimed_oldest_month = seniors.filter(is_claimed=True).aggregate(oldest_month=Min('claimed_date'))
    claimed_latest_month = seniors.filter(is_claimed=True).aggregate(latest_month=Max('claimed_date'))
    total_claimed_amount = seniors.filter(is_claimed=True).aggregate(total_amount=Sum('allowance_amount'))
    unclaimed_count = seniors.filter(is_claimed=False).count()

    for Claimed_senior in Claimed_accounts.order_by('last_name'):
        row = [
            Claimed_senior.OSCA_ID,
            Claimed_senior.last_name,
            Claimed_senior.first_name,
            Claimed_senior.claimed_date.strftime('%B %d, %Y'),
            Claimed_senior.allowance_type, 
            Claimed_senior.allowance_amount,
        ]
        Claimed_data.append(row)

    Claimed_Table = Table(Claimed_data)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    for i in range(1, len(Claimed_data)): 
        if Claimed_data[i][-1] == 'Claimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        elif Claimed_data[i][-1] == 'Unclaimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    Claimed_Table.setStyle(TableStyle(style))



    Unclaimed_data = [['OSCA ID', 'Last Name','First Name', 'Last Claimed', 'Phone Number', 'Address']]
    Unclaimed_accounts = seniors.filter(is_claimed=False)

    for Unclaimed_senior in Unclaimed_accounts.order_by('-is_claimed', 'last_name'):
        row = [
            Unclaimed_senior.OSCA_ID,
            Unclaimed_senior.last_name,
            Unclaimed_senior.first_name,
            Unclaimed_senior.claimed_date.strftime('%B %d, %Y') if Unclaimed_senior.claimed_date else "None",
            Unclaimed_senior.address,
            Unclaimed_senior.phone_number,
        ]
        Unclaimed_data.append(row)

    Unclaimed_Table = Table(Unclaimed_data)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    for i in range(1, len(Unclaimed_data)): 
        if Unclaimed_data[i][-1] == 'Claimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        elif Unclaimed_data[i][-1] == 'Unclaimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    Unclaimed_Table.setStyle(TableStyle(style))

    pdf = SimpleDocTemplate(response, pagesize=letter)
    left_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'mnl_logo.jpg')
    right_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'brgy_logo.jpg')

    left_image = Image(left_image_path, width=100, height=100)
    right_image = Image(right_image_path, width=100, height=100)

    header_text = """
    <b>REPUBLIC OF THE PHILIPPINES</b><br/>
    <b>CITY OF MANILA</b><br/>
    <b>BRGY. 558, ZONE 55</b>
    """

    header_text_with_margin = f'{header_text}<br/><br/>'

    header_style = ParagraphStyle(
        'Header',
        parent=getSampleStyleSheet()['Heading1'],
        alignment=1,  
        fontSize=14,
    )

    header = Paragraph(header_text_with_margin, header_style)

    image_margin = 30

    header_table_data = [
        [left_image, Spacer(1, image_margin), header, Spacer(1, image_margin), right_image]
    ]

    header_table = Table(header_table_data, colWidths=[50, image_margin, None, image_margin, 50])

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    header_table.setStyle(header_table_style)

    pdf = SimpleDocTemplate(response, pagesize=letter)

    summary_report = [
        f'Total Claimed Seniors: {claimed_count}',
        f'Total Unclaimed Seniors: {unclaimed_count}',
        f'Total Allowance Amount: {total_claimed_amount["total_amount"]}',
        f'Oldest Claimed Date: {claimed_oldest_month["oldest_month"].strftime("%B %d, %Y") if claimed_oldest_month["oldest_month"] else "N/A"}',
        f'Latest Claimed Date: {claimed_latest_month["latest_month"].strftime("%B %d, %Y") if claimed_latest_month["latest_month"] else "N/A"}',
        '',
    ]

    summary_report_paragraphs = [Paragraph(line, getSampleStyleSheet()['Normal']) for line in summary_report]

    summary_report_margin = 30
    summary_report_with_margin = [Spacer(1, summary_report_margin)] + summary_report_paragraphs
    table_margin = 20
    
    deleted_accounts_data = [['OSCA ID', 'Last Name', 'First Name', 'Registered Date', 'Deletion Date', 'Deletion Reason']]

    deleted_accounts = seniors.filter(date_of_deletion__isnull=False)

    for deleted_senior in deleted_accounts.order_by('-date_of_deletion', 'last_name'):
        deleted_row = [
            deleted_senior.OSCA_ID,
            deleted_senior.last_name,
            deleted_senior.first_name,
            deleted_senior.created.strftime('%Y-%m-%d') if deleted_senior.created else '',
            deleted_senior.date_of_deletion.strftime('%Y-%m-%d') if deleted_senior.date_of_deletion else '',
            deleted_senior.deletion_reason,
        ]
        deleted_accounts_data.append(deleted_row)

    if len(deleted_accounts_data) > 1:
        deleted_accounts_table = Table(deleted_accounts_data)

        deleted_accounts_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]

        deleted_accounts_table.setStyle(TableStyle(deleted_accounts_style))

        title_style = ParagraphStyle(
            'Title',
            parent=getSampleStyleSheet()['Heading2'],
            alignment=1,  
        )

        claimed_title = Paragraph("Claimed Senior Citizens", title_style)
        unclaimed_title = Paragraph("Unclaimed Senior Citizens", title_style)
        deleted_title = Paragraph("Deleted Senior Citizens", title_style)

        pdf_elements = [header_table] + summary_report_with_margin

        if len(Claimed_data) > 1:
            pdf_elements += [Spacer(1, table_margin), claimed_title, Claimed_Table, PageBreak(), header_table]

        if len(Unclaimed_data) > 0:
            pdf_elements += [Spacer(1, table_margin), unclaimed_title, Unclaimed_Table, PageBreak(), header_table]

        pdf_elements += [Spacer(1, table_margin), deleted_title, deleted_accounts_table]

        pdf.build(pdf_elements)

        #seniors.update(is_claimed=False)
        #seniors_to_delete = seniors.filter(date_of_deletion__isnull=False)
        #seniors_to_delete.delete()
    else:

        title_style = ParagraphStyle(
            'Title',
            parent=getSampleStyleSheet()['Heading2'],
            alignment=1,  
        )

        claimed_title = Paragraph("Claimed Senior Citizens", title_style)
        unclaimed_title = Paragraph("Unclaimed Senior Citizens", title_style)

        pdf_elements = [header_table] + summary_report_with_margin

        if len(Claimed_data) > 1:
            pdf_elements += [Spacer(1, table_margin), claimed_title, Claimed_Table, PageBreak(), header_table]

        if len(Unclaimed_data) > 0:
            pdf_elements += [Spacer(1, table_margin), unclaimed_title, Unclaimed_Table]

        pdf.build(pdf_elements)
        #seniors.update(is_claimed=False)

    return response


def download_summary_reset(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="senior_list_report.pdf"'

    seniors = senior_list.objects.all()

    Claimed_accounts = seniors.filter(is_claimed=True)

    Claimed_data = [['OSCA ID', 'Last Name','First Name', 'Claimed Date', 'Allowance Type', 'Allowance Amount']]

    claimed_count = seniors.filter(is_claimed=True).count()
    claimed_oldest_month = seniors.filter(is_claimed=True).aggregate(oldest_month=Min('claimed_date'))
    claimed_latest_month = seniors.filter(is_claimed=True).aggregate(latest_month=Max('claimed_date'))
    total_claimed_amount = seniors.filter(is_claimed=True).aggregate(total_amount=Sum('allowance_amount'))
    unclaimed_count = seniors.filter(is_claimed=False).count()

    for Claimed_senior in Claimed_accounts.order_by('last_name'):
        row = [
            Claimed_senior.OSCA_ID,
            Claimed_senior.last_name,
            Claimed_senior.first_name,
            Claimed_senior.claimed_date.strftime('%B %d, %Y'),
            Claimed_senior.allowance_type, 
            Claimed_senior.allowance_amount,
        ]
        Claimed_data.append(row)

    Claimed_Table = Table(Claimed_data)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    for i in range(1, len(Claimed_data)): 
        if Claimed_data[i][-1] == 'Claimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        elif Claimed_data[i][-1] == 'Unclaimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    Claimed_Table.setStyle(TableStyle(style))



    Unclaimed_data = [['OSCA ID', 'Last Name','First Name', 'Last Claimed', 'Phone Number', 'Address']]
    Unclaimed_accounts = seniors.filter(is_claimed=False)

    for Unclaimed_senior in Unclaimed_accounts.order_by('-is_claimed', 'last_name'):
        row = [
            Unclaimed_senior.OSCA_ID,
            Unclaimed_senior.last_name,
            Unclaimed_senior.first_name,
            Unclaimed_senior.claimed_date.strftime('%B %d, %Y') if Unclaimed_senior.claimed_date else "None",
            Unclaimed_senior.address,
            Unclaimed_senior.phone_number,
        ]
        Unclaimed_data.append(row)

    Unclaimed_Table = Table(Unclaimed_data)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    for i in range(1, len(Unclaimed_data)): 
        if Unclaimed_data[i][-1] == 'Claimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        elif Unclaimed_data[i][-1] == 'Unclaimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    Unclaimed_Table.setStyle(TableStyle(style))

    pdf = SimpleDocTemplate(response, pagesize=letter)
    left_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'mnl_logo.jpg')
    right_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'brgy_logo.jpg')

    left_image = Image(left_image_path, width=100, height=100)
    right_image = Image(right_image_path, width=100, height=100)

    header_text = """
    <b>REPUBLIC OF THE PHILIPPINES</b><br/>
    <b>CITY OF MANILA</b><br/>
    <b>BRGY. 558, ZONE 55</b>
    """

    header_text_with_margin = f'{header_text}<br/><br/>'

    header_style = ParagraphStyle(
        'Header',
        parent=getSampleStyleSheet()['Heading1'],
        alignment=1,  
        fontSize=14,
    )

    header = Paragraph(header_text_with_margin, header_style)

    image_margin = 30

    header_table_data = [
        [left_image, Spacer(1, image_margin), header, Spacer(1, image_margin), right_image]
    ]

    header_table = Table(header_table_data, colWidths=[50, image_margin, None, image_margin, 50])

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    header_table.setStyle(header_table_style)

    pdf = SimpleDocTemplate(response, pagesize=letter)

    summary_report = [
        f'Total Claimed Seniors: {claimed_count}',
        f'Total Unclaimed Seniors: {unclaimed_count}',
        f'Total Allowance Amount: {total_claimed_amount["total_amount"]}',
        f'Oldest Claimed Date: {claimed_oldest_month["oldest_month"].strftime("%B %d, %Y") if claimed_oldest_month["oldest_month"] else "N/A"}',
        f'Latest Claimed Date: {claimed_latest_month["latest_month"].strftime("%B %d, %Y") if claimed_latest_month["latest_month"] else "N/A"}',
        '',
    ]

    summary_report_paragraphs = [Paragraph(line, getSampleStyleSheet()['Normal']) for line in summary_report]

    summary_report_margin = 30
    summary_report_with_margin = [Spacer(1, summary_report_margin)] + summary_report_paragraphs
    table_margin = 20
    
    deleted_accounts_data = [['OSCA ID', 'Last Name', 'First Name', 'Registered Date', 'Deletion Date', 'Deletion Reason']]

    deleted_accounts = seniors.filter(date_of_deletion__isnull=False)

    for deleted_senior in deleted_accounts.order_by('-date_of_deletion', 'last_name'):
        deleted_row = [
            deleted_senior.OSCA_ID,
            deleted_senior.last_name,
            deleted_senior.first_name,
            deleted_senior.created.strftime('%Y-%m-%d') if deleted_senior.created else '',
            deleted_senior.date_of_deletion.strftime('%Y-%m-%d') if deleted_senior.date_of_deletion else '',
            deleted_senior.deletion_reason,
        ]
        deleted_accounts_data.append(deleted_row)

    if len(deleted_accounts_data) > 1:
        deleted_accounts_table = Table(deleted_accounts_data)

        deleted_accounts_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]

        deleted_accounts_table.setStyle(TableStyle(deleted_accounts_style))

        title_style = ParagraphStyle(
            'Title',
            parent=getSampleStyleSheet()['Heading2'],
            alignment=1,  
        )

        claimed_title = Paragraph("Claimed Senior Citizens", title_style)
        unclaimed_title = Paragraph("Unclaimed Senior Citizens", title_style)
        deleted_title = Paragraph("Deleted Senior Citizens", title_style)

        pdf_elements = [header_table] + summary_report_with_margin

        if len(Claimed_data) > 1:
            pdf_elements += [Spacer(1, table_margin), claimed_title, Claimed_Table, PageBreak(), header_table]

        if len(Unclaimed_data) > 0:
            pdf_elements += [Spacer(1, table_margin), unclaimed_title, Unclaimed_Table, PageBreak(), header_table]

        pdf_elements += [Spacer(1, table_margin), deleted_title, deleted_accounts_table]

        pdf.build(pdf_elements)

        seniors.update(is_claimed=False)
        seniors_to_delete = seniors.filter(date_of_deletion__isnull=False)
        seniors_to_delete.delete()
    else:

        title_style = ParagraphStyle(
            'Title',
            parent=getSampleStyleSheet()['Heading2'],
            alignment=1,  
        )

        claimed_title = Paragraph("Claimed Senior Citizens", title_style)
        unclaimed_title = Paragraph("Unclaimed Senior Citizens", title_style)

        pdf_elements = [header_table] + summary_report_with_margin

        if len(Claimed_data) > 1:
            pdf_elements += [Spacer(1, table_margin), claimed_title, Claimed_Table, PageBreak(), header_table]

        if len(Unclaimed_data) > 0:
            pdf_elements += [Spacer(1, table_margin), unclaimed_title, Unclaimed_Table]

        pdf.build(pdf_elements)
        seniors.update(is_claimed=False)

    return response

def download_summary_claimed(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="senior_list_report.pdf"'

    seniors = senior_list.objects.all() 
    Claimed_accounts = seniors.filter(is_claimed=True)

    claimed_data = [['OSCA ID', 'Last Name', 'First Name', 'Claimed Date', 'Allowance Type', 'Allowance Amount']]

    for senior in Claimed_accounts.order_by('last_name'):
        row = [
            senior.OSCA_ID,
            senior.last_name,
            senior.first_name,
            senior.claimed_date.strftime('%B %d, %Y') if senior.is_claimed else '', 
            senior.allowance_type,
            senior.allowance_amount,
        ]
        claimed_data.append(row)

    claimed_table = Table(claimed_data)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    for i in range(1, len(claimed_data)):
        if claimed_data[i][-1] == 'Claimed' or claimed_data[i][-1] == 'Unclaimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    claimed_table.setStyle(TableStyle(style))

    pdf = SimpleDocTemplate(response, pagesize=letter)

    left_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'mnl_logo.jpg')
    right_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'brgy_logo.jpg')

    left_image = Image(left_image_path, width=100, height=100)
    right_image = Image(right_image_path, width=100, height=100)

    header_text = """
    <b>REPUBLIC OF THE PHILIPPINES</b><br/>
    <b>CITY OF MANILA</b><br/>
    <b>BRGY. 558, ZONE 55</b>
    """

    header_text_with_margin = f'{header_text}<br/><br/>'

    header_style = ParagraphStyle(
        'Header',
        parent=getSampleStyleSheet()['Heading1'],
        alignment=1,
        fontSize=14,
    )

    header = Paragraph(header_text_with_margin, header_style)

    image_margin = 30

    header_table_data = [
        [left_image, Spacer(1, image_margin), header, Spacer(1, image_margin), right_image]
    ]

    header_table = Table(header_table_data, colWidths=[50, image_margin, None, image_margin, 50])

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    header_table.setStyle(header_table_style)

    title_style = ParagraphStyle(
        'Title',
        parent=getSampleStyleSheet()['Heading2'],
        alignment=1,
    )

    claimed_title = Paragraph("Claimed Senior Citizens", title_style)


    # Build the PDF document
    pdf.build([header_table, Spacer(1, 20),claimed_title, claimed_table])

    return response


def download_summary_unclaimed(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="senior_list_report.pdf"'

    seniors = senior_list.objects.all()

    Unclaimed_data = [['OSCA ID', 'Last Name', 'First Name', 'Last Claimed', 'Phone Number', 'Address']]
    Unclaimed_accounts = seniors.filter(is_claimed=False)

    for Unclaimed_senior in Unclaimed_accounts.order_by('-is_claimed', 'last_name'):
        row = [
            Unclaimed_senior.OSCA_ID,
            Unclaimed_senior.last_name,
            Unclaimed_senior.first_name,
            Unclaimed_senior.claimed_date.strftime('%B %d, %Y') if Unclaimed_senior.claimed_date else "None",
            Unclaimed_senior.phone_number,
            Unclaimed_senior.address,
        ]
        Unclaimed_data.append(row)

    Unclaimed_Table = Table(Unclaimed_data)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    for i in range(1, len(Unclaimed_data)):
        if Unclaimed_data[i][-1] == 'Claimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        elif Unclaimed_data[i][-1] == 'Unclaimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    Unclaimed_Table.setStyle(TableStyle(style))

    pdf = SimpleDocTemplate(response, pagesize=letter)

    left_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'mnl_logo.jpg')
    right_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'brgy_logo.jpg')

    left_image = Image(left_image_path, width=100, height=100)
    right_image = Image(right_image_path, width=100, height=100)

    header_text = """
    <b>REPUBLIC OF THE PHILIPPINES</b><br/>
    <b>CITY OF MANILA</b><br/>
    <b>BRGY. 558, ZONE 55</b>
    """

    header_text_with_margin = f'{header_text}<br/><br/>'

    header_style = ParagraphStyle(
        'Header',
        parent=getSampleStyleSheet()['Heading1'],
        alignment=1,
        fontSize=14,
    )

    header = Paragraph(header_text_with_margin, header_style)

    image_margin = 30

    header_table_data = [
        [left_image, Spacer(1, image_margin), header, Spacer(1, image_margin), right_image]
    ]

    header_table = Table(header_table_data, colWidths=[50, image_margin, None, image_margin, 50])

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    header_table.setStyle(header_table_style)

    title_style = ParagraphStyle(
        'Title',
        parent=getSampleStyleSheet()['Heading2'],
        alignment=1,
    )

    unclaimed_title = Paragraph("Unclaimed Senior Citizens", title_style)

    table_margin = 10

    pdf.build([header_table, Spacer(1, table_margin), unclaimed_title, Unclaimed_Table])

    return response
    

def download_summary_deleted(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="senior_list_report.pdf"'

    seniors = senior_list.objects.all()

    deleted_accounts_data = [['OSCA ID', 'Last Name', 'First Name', 'Registered Date', 'Deletion Date', 'Deletion Reason']]

    deleted_accounts = seniors.filter(date_of_deletion__isnull=False)

    for deleted_senior in deleted_accounts.order_by('-date_of_deletion', 'last_name'):
        deleted_row = [
            deleted_senior.OSCA_ID,
            deleted_senior.last_name,
            deleted_senior.first_name,
            deleted_senior.created.strftime('%Y-%m-%d') if deleted_senior.created else '',
            deleted_senior.date_of_deletion.strftime('%Y-%m-%d') if deleted_senior.date_of_deletion else '',
            deleted_senior.deletion_reason,
        ]
        deleted_accounts_data.append(deleted_row)

    deleted_accounts_table = Table(deleted_accounts_data)

    deleted_accounts_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    deleted_accounts_table.setStyle(TableStyle(deleted_accounts_style))

    pdf = SimpleDocTemplate(response, pagesize=letter)

    left_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'mnl_logo.jpg')
    right_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'brgy_logo.jpg')

    left_image = Image(left_image_path, width=100, height=100)
    right_image = Image(right_image_path, width=100, height=100)

    header_text = """
    <b>REPUBLIC OF THE PHILIPPINES</b><br/>
    <b>CITY OF MANILA</b><br/>
    <b>BRGY. 558, ZONE 55</b>
    """

    header_text_with_margin = f'{header_text}<br/><br/>'

    header_style = ParagraphStyle(
        'Header',
        parent=getSampleStyleSheet()['Heading1'],
        alignment=1,
        fontSize=14,
    )

    header = Paragraph(header_text_with_margin, header_style)

    image_margin = 30

    header_table_data = [
        [left_image, Spacer(1, image_margin), header, Spacer(1, image_margin), right_image]
    ]

    header_table = Table(header_table_data, colWidths=[50, image_margin, None, image_margin, 50])

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    header_table.setStyle(header_table_style)

    title_style = ParagraphStyle(
        'Title',
        parent=getSampleStyleSheet()['Heading2'],
        alignment=1,
    )

    deleted_title = Paragraph("Deleted Senior Citizens", title_style)

    table_margin = 10

    pdf_elements = [header_table, Spacer(1, table_margin), deleted_title, deleted_accounts_table]

    pdf.build(pdf_elements)

    return response


def download_summary_senior(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="senior_list_report.pdf"'

    seniors = senior_list.objects.all()

    senior_data = [['OSCA ID', 'Last Name', 'First Name', 'Last Claimed', 'Phone Number', 'Address', 'Status']]

    for senior in seniors.order_by('-is_claimed', 'last_name'):
        status = 'Claimed' if senior.is_claimed else 'Unclaimed'
        row = [
            senior.OSCA_ID,
            senior.last_name,
            senior.first_name,
            senior.claimed_date.strftime('%B %d, %Y') if senior.claimed_date else "None",
            senior.phone_number,
            senior.address,
            status,
        ]
        senior_data.append(row)

    senior_Table = Table(senior_data)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    for i in range(1, len(senior_data)):
        if senior_data[i][-1] == 'Claimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        elif senior_data[i][-1] == 'Unclaimed':
            style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    senior_Table.setStyle(TableStyle(style))

    pdf = SimpleDocTemplate(response, pagesize=letter)

    left_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'mnl_logo.jpg')
    right_image_path = os.path.join(settings.STATIC_ROOT, 'image', 'brgy_logo.jpg')

    left_image = Image(left_image_path, width=100, height=100)
    right_image = Image(right_image_path, width=100, height=100)

    header_text = """
    <b>REPUBLIC OF THE PHILIPPINES</b><br/>
    <b>CITY OF MANILA</b><br/>
    <b>BRGY. 558, ZONE 55</b>
    """

    header_text_with_margin = f'{header_text}<br/><br/>'

    header_style = ParagraphStyle(
        'Header',
        parent=getSampleStyleSheet()['Heading1'],
        alignment=1,
        fontSize=14,
    )

    header = Paragraph(header_text_with_margin, header_style)

    image_margin = 30

    header_table_data = [
        [left_image, Spacer(1, image_margin), header, Spacer(1, image_margin), right_image]
    ]

    header_table = Table(header_table_data, colWidths=[50, image_margin, None, image_margin, 50])

    header_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    header_table.setStyle(header_table_style)

    title_style = ParagraphStyle(
        'Title',
        parent=getSampleStyleSheet()['Heading2'],
        alignment=1,
    )

    senior_title = Paragraph("List of Senior Citizens in Barangay 558", title_style)

    table_margin = 10

    pdf_elements = [header_table, Spacer(1, table_margin), senior_title, senior_Table]

    pdf.build(pdf_elements)

    return response

def index(request):
    return render(request, 'index.html'  )

def profile_page(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile_page.html', context)

def index(request):
    page = 'index'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'index.html', {'page': page})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(update_page)
        else:
            messages.error(request, 'Invalid Password')
            
    context = {'page': page}
    return render(request, 'index.html', context)

def home_page(request):
    return render(request, 'home_page.html'  )

#def register_page(request):
#    return render(request, 'register_page.html')

def main_page(request):
    return render(request, 'main.html')

#def register_page(request):
#    form = register_form()
#    if request.method == 'POST':
#        form = register_form(request.POST, request.FILES)
#        if form.is_valid():
#            seniors = form.save(commit=False)
#            seniors.status = True 
#            seniors.save()
#
#            return redirect('preview', id=seniors.id)
#
#    context = {'form': form}
#    return render(request, 'register_page.html', context)

def update_page(request):
    status_filter = request.GET.get('status_filter', 'all')

    if status_filter == 'active':
        seniors = senior_list.objects.filter(status=True)
    elif status_filter == 'inactive':
        seniors = senior_list.objects.filter(status=False)
    else:
        seniors = senior_list.objects.all()

    total_active = seniors.filter(status=True).count()
    total_inactive = seniors.filter(status=False).count()

    seniors = seniors.order_by('last_name')

    return render(request, 'update_page.html', {'seniors': seniors, 'total_active': total_active, 'total_inactive': total_inactive})

def add_senior(request):
    result = None
    view_info_link = None

    if request.method == 'POST':
        osca_id = request.POST.get('osca_id')
        try:
            senior = osca_list.objects.get(OSCA_ID=osca_id)
            result = f'OSCA ID is valid. '
            view_info_link = reverse('osca_preview', args=[senior.id])
        except osca_list.DoesNotExist:
            result = f'NOT FOUND!'

    return JsonResponse({'result': result, 'view_info_link': view_info_link})

def osca_preview(request, id):
    senior = get_object_or_404(osca_list, id=id)
    return render(request, 'osca_preview.html', {'senior': senior})

def update_viewinfo_page(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'update_viewinfo_page.html', {'seniors': seniors})

def updated_claim(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'updated_claim.html', {'seniors': seniors})

def add_senior_list(request, osca_id):
    try:
        if senior_list.objects.filter(OSCA_ID=osca_id).exists():
            messages.warning(request, 'Senior with this OSCA ID already exists.')
            return redirect('update_page')

        osca_record = osca_list.objects.get(OSCA_ID=osca_id)

        senior_record = senior_list(
            first_name=osca_record.first_name,
            last_name=osca_record.last_name,
            middle_name=osca_record.middle_name,
            suffix=osca_record.suffix,
            age=osca_record.age,
            sex=osca_record.sex,
            birth_date=osca_record.birth_date,
            barangay=osca_record.barangay,
            address=osca_record.address,
            phone_number=osca_record.phone_number,
            OSCA_ID=osca_record.OSCA_ID,
        )
        senior_record.save()
        messages.success(request, 'Senior added successfully.')
        return redirect('update_page')
    
    except osca_list.DoesNotExist:
        messages.error(request, 'OSCA record not found.')
        return render(request, 'update_page.html', {'error_message': 'OSCA record not found'}) 
    
def delete(request, id):
    seniors = senior_list.objects.get(id=id)

    if request.method == 'POST':
        selected_deletion_reason = request.POST.get('selected_deletion_reason')
        if selected_deletion_reason:
            seniors.deletion_reason = selected_deletion_reason
            seniors.status = False
            seniors.date_of_deletion = timezone.now()
            seniors.save()
            return HttpResponseRedirect('/update_page/')  

    return render(request, 'update_viewinfo_page.html', {'seniors': seniors})

def edit(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'edit.html', {'seniors': seniors})

def update(request, id):
    seniors = senior_list.objects.get(id=id)

    if request.method == 'POST':
        temporary_image_data_url = request.POST.get('temporary_image', '')
        if temporary_image_data_url:
            _, temporary_image_base64 = temporary_image_data_url.split(',')
            temporary_image = ContentFile(base64.b64decode(temporary_image_base64), name=f'temporary_image.png')

            if seniors.senior_image and os.path.exists(seniors.senior_image.path):
                os.remove(seniors.senior_image.path)

            current_date = datetime.now().strftime("%Y%m%d")
            new_image_name = os.path.join('media', f'updated_image_{seniors.OSCA_ID}_{current_date}.png')
            seniors.senior_image.save(new_image_name, temporary_image, save=True)

        elif 'senior_image' in request.FILES:
            if seniors.senior_image:
                os.remove(seniors.senior_image.path)

            uploaded_image = request.FILES['senior_image']

            current_date = datetime.now().strftime("%Y%m%d%H%M%S")
            new_image_name = f'updated_image_{seniors.OSCA_ID}_{current_date}.png'
            seniors.senior_image.save(new_image_name, uploaded_image)

        seniors.last_name = request.POST.get('Lastname')
        seniors.first_name = request.POST.get('Firstname')
        seniors.middle_name = request.POST.get('Middlename')
        seniors.suffix = request.POST.get('Suffix')
        seniors.age = request.POST.get('Age')
        seniors.sex = request.POST.get('sex')
        seniors.address = request.POST.get('Adress')
        seniors.phone_number = request.POST.get('phone_number')
        seniors.status = True
        seniors.save()

    context = {'seniors': seniors}
    return render(request, 'update_viewinfo_page.html', context)



def edit_claim(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'edit_claim.html', {'seniors': seniors})

def update_claim(request, id):
    seniors = senior_list.objects.get(id=id)

    if request.method == 'POST':
        temporary_image_data_url = request.POST.get('temporary_image', '')
        if temporary_image_data_url:
            _, temporary_image_base64 = temporary_image_data_url.split(',')
            temporary_image = ContentFile(base64.b64decode(temporary_image_base64), name=f'temporary_image.png')

            if seniors.senior_image and os.path.exists(seniors.senior_image.path):
                os.remove(seniors.senior_image.path)

            current_date = datetime.now().strftime("%Y%m%d")
            new_image_name = os.path.join('media', f'updated_image_{seniors.OSCA_ID}_{current_date}.png')
            seniors.senior_image.save(new_image_name, temporary_image, save=True)

        elif 'senior_image' in request.FILES:
            if seniors.senior_image:
                os.remove(seniors.senior_image.path)

            uploaded_image = request.FILES['senior_image']

            current_date = datetime.now().strftime("%Y%m%d%H%M%S")
            new_image_name = f'updated_image_{seniors.OSCA_ID}_{current_date}.png'
            seniors.senior_image.save(new_image_name, uploaded_image)

        seniors.last_name = request.POST.get('Lastname')
        seniors.first_name = request.POST.get('Firstname')
        seniors.middle_name = request.POST.get('Middlename')
        seniors.suffix = request.POST.get('Suffix')
        seniors.age = request.POST.get('Age')
        seniors.sex = request.POST.get('sex')
        seniors.address = request.POST.get('Adress')
        seniors.phone_number = request.POST.get('phone_number')
        seniors.status = True
        seniors.save()

        if not seniors.senior_image:
            return redirect('claim_page')
    
    context = {'seniors': seniors}
    return render(request, 'updated_claim.html', context)
    

def search(request):
    if 'q' in request.GET:
        q= request.GET['q']
        #seniors= senior_list.objects.filter(last_name__icontains=q)
        multiple_q=Q(Q(last_name__icontains=q) | Q(first_name__icontains=q))
        seniors = senior_list.objects.filter(multiple_q)
    else:
        seniors=senior_list.objects.all()
    context={'seniors': seniors}
    return render(request, 'update_page.html', context)

def search1(request):
    if 'q' in request.GET:
        q= request.GET['q']
        #seniors= senior_list.objects.filter(last_name__icontains=q)
        multiple_q=Q(Q(last_name__icontains=q) | Q(first_name__icontains=q))
        seniors = senior_list.objects.filter(multiple_q)
    else:
        seniors=senior_list.objects.all()
    context={'seniors': seniors}
    return render(request, 'claim_page.html', context)

def claim_page(request):
    status_filter = request.GET.get('status_filter', 'all')
    is_claimed_filter = request.GET.get('is_claimed', 'all')

    if status_filter == 'active':
        seniors = senior_list.objects.filter(status=True)
    elif status_filter == 'inactive':
        seniors = senior_list.objects.filter(status=False)
    else:
        seniors = senior_list.objects.all()

    if is_claimed_filter == 'claimed':
        seniors = seniors.filter(is_claimed=True)
    elif is_claimed_filter == 'not_claimed':
        seniors = seniors.filter(is_claimed=False)

    seniors = seniors.order_by('last_name')

    total_active = seniors.filter(status=True).count()
    total_inactive = seniors.filter(status=False).count()

    return render(request, 'claim_page.html', {'seniors': seniors, 'total_active': total_active, 'total_inactive': total_inactive})



def claim_detail_page(request, id):
    seniors = senior_list.objects.get(id=id)
    choices = seniors._meta.get_field('allowance_type').choices
    return render(request, 'claim_detail_page.html', {'seniors': seniors, 'choices': choices})

def claimed_success(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'claimed_success.html', {'seniors': seniors})

def claimed_succesfully(request, id):
    seniors = get_object_or_404(senior_list, pk=id)
    seniors.is_claimed = True
    seniors.claimed_date = timezone.now()
    seniors.save()

    context = {
        'last_name': seniors.last_name,
        'first_name': seniors.first_name,
        'middle_name': seniors.middle_name,
        'OSCA_ID': seniors.OSCA_ID,
        'claimed_date': seniors.claimed_date,
    }
    return render(request, 'claimed_success.html', context)


def claim_verify_page(request):
    claimed_seniors = senior_list.objects.filter(is_claimed=True).order_by('last_name')
    unclaimed_seniors = senior_list.objects.filter(is_claimed=False).order_by('last_name')
    seniors = list(claimed_seniors) + list(unclaimed_seniors)

    return render(request, 'claim_verify_page.html', {'seniors': seniors})

from django.db.models import Count, Q
from django.db.models import Min
from django.db.models.functions import TruncMonth

def claim_summary_page(request):
    latest_claimed_entry = senior_list.objects.filter(is_claimed=True).order_by('-claimed_date').first()
    oldest_claimed_entry = senior_list.objects.filter(is_claimed=True).order_by('claimed_date').first()

    counts = senior_list.objects.aggregate(
        claimed_count=Count('pk', filter=Q(is_claimed=True)),
        unclaimed_count=Count('pk', filter=Q(is_claimed=False, date_of_deletion__isnull=True)),
        deleted_count=Count('pk', filter=Q(status=False, date_of_deletion__isnull=False)),
        overall_count=Count('pk', filter=Q(date_of_deletion__isnull=True)),
    )

    if latest_claimed_entry and oldest_claimed_entry:
        show_one_month = (
            latest_claimed_entry.claimed_date.month == oldest_claimed_entry.claimed_date.month and
            latest_claimed_entry.claimed_date.year == oldest_claimed_entry.claimed_date.year
        )
    else:
        show_one_month = False

    context = {
        'latest_claimed_entry': latest_claimed_entry,
        'oldest_claimed_entry': oldest_claimed_entry,
        'claimed_count': counts['claimed_count'],
        'unclaimed_count': counts['unclaimed_count'],
        'deleted_count': counts['deleted_count'],
        'overall_count': counts['overall_count'],
        'show_one_month': show_one_month,
    }

    return render(request, 'claim_summary_page.html', context)



def sms(request):
    messages = SMSMessage.objects.all()
    context={'messages':messages}

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        body_message = request.POST.get('body_message')

        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER

        client = Client(account_sid, auth_token)

        try:
            message = client.messages.create(
                body=body_message,
                from_=twilio_phone_number,
                to=phone_number
            )

            current_date = timezone.now()

            SMSMessage.objects.create(
                from_number=settings.TWILIO_PHONE_NUMBER,
                body=body_message,
                timestamp=current_date
            )

            response_data = {
                'status': 'success',
                'message': f'Message sent successfully! SID: {message.sid}'
            }
        except Exception as e:
            response_data = {
                'status': 'error',
                'message': f'Failed to send message. Error: {str(e)}'
            }

        return JsonResponse(response_data)

    return render(request, 'sms.html', context )

def clear_messages(request):
    if request.method == 'POST':
        SMSMessage.objects.all().delete()
    return render(request, 'sms.html')

def delete_individual_message(request, message_id):
    message = SMSMessage.objects.get(id=message_id)
    message.delete()
    return redirect(sms)
    

def preview(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'preview.html', {'seniors': seniors})

def camera(request):
    return render(request, 'capture_image.html')

@csrf_exempt
def capture_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            image_data = data.get('image_data', '')

            image_data = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            img = cv2.resize(img, (256, 256))

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"captured_image_{timestamp}.png"
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            cv2.imwrite(filepath, img)
            
            return JsonResponse({'image_path': filepath})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

from django.core.files.base import ContentFile

@csrf_exempt
def facial_recognition(request, id):
    seniors = senior_list.objects.get(id=id)

    if request.method == 'POST':
        captured_image_data_url = request.POST.get('captured_image', '')

        _, captured_image_base64 = captured_image_data_url.split(',')
        captured_image = np.frombuffer(base64.b64decode(captured_image_base64), np.uint8)

        captured_image_np = cv2.imdecode(captured_image, -1)

        if captured_image_np is None:
            return JsonResponse({'error': 'Unable to load the image.'})

        known_face_encoding = get_known_face_encoding(seniors.senior_image.path)

        face_locations = face_recognition.face_locations(captured_image_np)
        captured_face_encodings = face_recognition.face_encodings(captured_image_np, face_locations)

        for captured_face_encoding in captured_face_encodings:
            match = compare_faces(known_face_encoding, captured_face_encoding)

            if match:
                seniors.status = True
                seniors.is_claimed = True
                seniors.claimed_date = timezone.now()
                proof_image_name = f"proof_{seniors.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.png"
                proof_image_path = os.path.join('proof/', proof_image_name)
                proof_image_content = ContentFile(cv2.imencode('.png', captured_image_np)[1].tobytes())
                seniors.proof_of_claiming.save(proof_image_name, proof_image_content, save=True)

                seniors.save()

                return JsonResponse({'match': True, 'proof_of_claiming_url': seniors.proof_of_claiming.url})

    return JsonResponse({'match': False})

def get_known_face_encoding(image_path):

    known_image = face_recognition.load_image_file(image_path)

    known_face_encoding = face_recognition.face_encodings(known_image)

    if known_face_encoding:
        return known_face_encoding[0] 
    else:
        return None

def compare_faces(known_encoding, captured_encoding):
    threshold = 0.5
    distance = face_recognition.face_distance([known_encoding], captured_encoding)

    return distance <= threshold


def camera_page(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'camera.html', {'seniors': seniors})

def match(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'match.html', {'seniors': seniors})

def deleted(request, id):
    seniors = senior_list.objects.get(id=id)
    return render(request, 'deleted.html', {'seniors': seniors})

def check_osca_id(request):
    osca_id = request.GET.get('osca_id', '')
    is_taken = senior_list.objects.filter(OSCA_ID=osca_id).exists()
    return JsonResponse({'is_taken': is_taken})

def save_allowance(request, id):
    if request.method == 'POST':
        seniors = get_object_or_404(senior_list, id=id)

        allowance_type = request.POST.get('allowanceType')
        allowance_amount = request.POST.get('allowanceAmount')

        seniors.allowance_type = allowance_type
        seniors.allowance_amount = allowance_amount
        seniors.save()

        return JsonResponse({'status': 'success', 'id': seniors.id})

    return JsonResponse({'status': 'error'})

def retrieve_entry(request, id):
    seniors = get_object_or_404(senior_list, id=id)

    if request.method == 'POST':
        seniors.date_of_deletion = None
        seniors.deletion_reason = None
        seniors.status = True
        seniors.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
