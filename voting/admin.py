from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
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
        """Handle Excel/CSV file upload and import voters using pandas"""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                overwrite = form.cleaned_data['overwrite_existing']
                
                try:
                    # Get file extension
                    file_name = excel_file.name.lower()
                    
                    # Validate file type
                    if not (file_name.endswith('.xlsx') or file_name.endswith('.xls') or file_name.endswith('.csv')):
                        messages.error(request, "Please upload a valid Excel (.xlsx, .xls) or CSV file")
                        return redirect('.')
                    
                    # Validate file size (max 10MB)
                    if excel_file.size > 10 * 1024 * 1024:
                        messages.error(request, "File size too large. Maximum size is 10MB.")
                        return redirect('.')
                    
                    # Read file into BytesIO for pandas
                    file_content = BytesIO(excel_file.read())
                    
                    # Read with pandas based on file type
                    try:
                        if file_name.endswith('.csv'):
                            df = pd.read_csv(file_content)
                        else:
                            # Try openpyxl first, fallback to xlrd for .xls
                            try:
                                df = pd.read_excel(file_content, engine='openpyxl')
                            except:
                                file_content.seek(0)  # Reset file pointer
                                df = pd.read_excel(file_content, engine='xlrd')
                    except Exception as e:
                        messages.error(request, f"Could not read file: {str(e)}. Please ensure it's a valid Excel or CSV file.")
                        return redirect('.')
                    
                    # Validate required columns
                    required_columns = ['voter_no', 'name']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        messages.error(
                            request,
                            f"Missing required columns: {', '.join(missing_columns)}. Expected: voter_no, name, house (optional)"
                        )
                        return redirect('.')
                    
                    # Clean data
                    df = df.fillna('')  # Replace NaN with empty string
                    df['voter_no'] = df['voter_no'].astype(str).str.strip()
                    df['name'] = df['name'].astype(str).str.strip()
                    
                    if 'house' in df.columns:
                        df['house'] = df['house'].astype(str).str.strip()
                    else:
                        df['house'] = ''
                    
                    # Remove empty rows
                    df = df[df['voter_no'] != '']
                    df = df[df['name'] != '']
                    
                    if len(df) == 0:
                        messages.warning(request, "No valid data found in file")
                        return redirect('.')
                    
                    created_count = 0
                    updated_count = 0
                    skipped_count = 0
                    errors = []
                    
                    # Import voters
                    with transaction.atomic():
                        for index, row in df.iterrows():
                            try:
                                voter_no = row['voter_no']
                                name = row['name']
                                house = row.get('house', '')
                                
                                # Validate
                                if not voter_no or not name:
                                    errors.append(f"Row {index + 2}: Missing voter_no or name")
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
                                errors.append(f"Row {index + 2}: {str(e)}")
                                skipped_count += 1
                    
                    # Success message
                    success_msg = f"Import completed: {created_count} created"
                    if overwrite and updated_count > 0:
                        success_msg += f", {updated_count} updated"
                    if skipped_count > 0:
                        success_msg += f", {skipped_count} skipped"
                    
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
                    return redirect('.')
        else:
            form = ExcelImportForm()
        
        context = {
            'form': form,
            'title': 'Import Voters from Excel/CSV',
            'site_title': 'Import Voters',
            'site_header': admin.site.site_header,
            'has_permission': True,
        }
        return render(request, 'admin/voters/import_excel.html', context)
    
    def download_template(self, request):
        """Download Excel template for voter import using pandas"""
        # Create sample data
        data = {
            'voter_no': ['V001', 'V002', 'V003'],
            'name': ['John Doe', 'Jane Smith', 'Mary Johnson'],
            'house': ['Red House', 'Blue House', 'Green House']
        }
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Voters Template')
            
            # Access the workbook to style headers
            workbook = writer.book
            worksheet = writer.sheets['Voters Template']
            
            # Style headers
            from openpyxl.styles import Font, PatternFill
            header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
            header_font = Font(bold=True)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
            
            # Adjust column widths
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 20
        
        output.seek(0)
        
        # Create response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=voters_template.xlsx'
        
        return response
    
    def export_voters(self, request, queryset):
        """Export selected voters to Excel using pandas"""
        # Prepare data
        data = []
        for voter in queryset:
            data.append({
                'voter_no': voter.voter_no,
                'name': voter.name,
                'house': voter.house,
                'has_voted': 'Yes' if voter.has_voted else 'No'
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Voters Export')
            
            # Access the workbook to style headers
            workbook = writer.book
            worksheet = writer.sheets['Voters Export']
            
            # Style headers
            from openpyxl.styles import Font, PatternFill
            header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
            header_font = Font(bold=True)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
            
            # Adjust column widths
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 20
            worksheet.column_dimensions['D'].width = 15
        
        output.seek(0)
        
        # Create response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=voters_export.xlsx'
        
        self.message_user(request, f"{len(data)} voters exported successfully")
        
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
