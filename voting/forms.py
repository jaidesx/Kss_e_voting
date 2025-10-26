from django import forms


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload an Excel file (.xlsx) with columns: voter_no, name, house',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )
    overwrite_existing = forms.BooleanField(
        label='Update existing voters',
        help_text='If checked, existing voters will be updated with new data. Otherwise, they will be skipped.',
        required=False,
        initial=False
    )
    
    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        
        # Check file extension
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError('Please upload a valid Excel file (.xlsx or .xls)')
        
        # Check file size (max 10MB)
        if excel_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('File size must be less than 10MB')
        
        return excel_file