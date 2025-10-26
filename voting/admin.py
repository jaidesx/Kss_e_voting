# voters/admin.py

from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
import openpyxl
from openpyxl import Workbook
from io import BytesIO
from .models import Voter, Vote
from .forms import ExcelImportForm


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ['voter_no', 'name', 'house', 'has_voted']
    list_filter = ['has_voted', 'house']
    search_fields = ['voter_no', 'name', 'house']
    readonly_fields = ['has_voted']
    list_per_page = 50
    
    actions = ['export_voters', 'mark_as_not_voted', 'delete_all_voters']
    
    change_list_template = "admin/voters/voter_changelist.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel), name='voters_voter_import_excel'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='voters_voter_download_template'),
        ]
        return custom_urls + urls
    
    def import_excel(self, request):
        """Handle Excel file upload and import voters"""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                overwrite = form.cleaned_data['overwrite_existing']
                
                try:
                    # Load workbook
                    wb = openpyxl.load_workbook(excel_file)
                    ws = wb.active
                    
                    created_count = 0
                    updated_count = 0
                    skipped_count = 0
                    errors = []
                    
                    # Start from row 2 (skip header)
                    with transaction.atomic():
                        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                            # Skip empty rows
                            if not any(row):
                                continue
                            
                            try:
                                voter_no = str(row[0]).strip() if row[0] else None
                                name = str(row[1]).strip() if row[1] else None
                                house = str(row[2]).strip() if row[2] else ''
                                
                                # Validate required fields
                                if not voter_no or not name:
                                    errors.append(f"Row {row_num}: Missing voter_no or name")
                                    skipped_count += 1
                                    continue
                                
                                # Check if voter exists
                                voter, created = Voter.objects.get_or_create(
                                    voter_no=voter_no,
                                    defaults={'name': name, 'house': house}
                                )
                                
                                if created:
                                    created_count += 1
                                elif overwrite:
                                    voter.name = name
                                    voter.house = house
                                    voter.save()
                                    updated_count += 1
                                else:
                                    skipped_count += 1
                                    
                            except Exception as e:
                                errors.append(f"Row {row_num}: {str(e)}")
                                skipped_count += 1
                    
                    # Success message
                    success_msg = f"Import completed: {created_count} created, {updated_count} updated, {skipped_count} skipped"
                    if errors:
                        success_msg += f" ({len(errors)} errors)"
                    
                    messages.success(request, success_msg)
                    
                    # Show errors if any
                    if errors:
                        for error in errors[:10]:  # Show first 10 errors
                            messages.warning(request, error)
                        if len(errors) > 10:
                            messages.warning(request, f"... and {len(errors) - 10} more errors")
                    
                    return redirect('..')
                    
                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")
        else:
            form = ExcelImportForm()
        
        context = {
            'form': form,
            'title': 'Import Voters from Excel',
            'site_title': 'Import Voters',
            'site_header': admin.site.site_header,
            'has_permission': True,
        }
        return render(request, 'admin/voters/import_excel.html', context)
    
    def download_template(self, request):
        """Download Excel template for voter import"""
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Voters Template"
        
        # Add headers
        headers = ['voter_no', 'name', 'house']
        ws.append(headers)
        
        # Style headers
        for cell in ws[1]:
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
        
        # Add sample data
        sample_data = [
            ['V001', 'John Doe', 'Red House'],
            ['V002', 'Jane Smith', 'Blue House'],
            ['V003', 'Mary Johnson', 'Green House'],
        ]
        for row in sample_data:
            ws.append(row)
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 20
        
        # Save to BytesIO
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        # Create response
        response = HttpResponse(
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=voters_template.xlsx'
        
        return response
    
    def export_voters(self, request, queryset):
        """Export selected voters to Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Voters Export"
        
        # Add headers
        headers = ['voter_no', 'name', 'house', 'has_voted']
        ws.append(headers)
        
        # Style headers
        for cell in ws[1]:
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
        
        # Add data
        for voter in queryset:
            ws.append([voter.voter_no, voter.name, voter.house, 'Yes' if voter.has_voted else 'No'])
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 15
        
        # Save to BytesIO
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        # Create response
        response = HttpResponse(
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=voters_export.xlsx'
        
        return response
    
    export_voters.short_description = "Export selected voters to Excel"
    
    def mark_as_not_voted(self, request, queryset):
        """Mark selected voters as not voted"""
        updated = queryset.update(has_voted=False)
        self.message_user(request, f"{updated} voters marked as not voted.")
    
    mark_as_not_voted.short_description = "Mark as not voted"
    
    def delete_all_voters(self, request, queryset):
        """Delete all voters (use with caution)"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} voters deleted.", messages.WARNING)
    
    delete_all_voters.short_description = "Delete selected voters"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'post', 'candidate', 'timestamp']
    list_filter = ['post', 'timestamp']
    search_fields = ['voter__name', 'voter__voter_no', 'candidate__name']
    readonly_fields = ['voter', 'post', 'candidate', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        # Prevent manual vote addition through admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent vote modification through admin
        return False