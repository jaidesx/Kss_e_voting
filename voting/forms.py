from django import forms


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel / CSV File',
        help_text='Upload an Excel (.xlsx, .xls) or CSV file.',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls,.csv'})
    )
    overwrite_existing = forms.BooleanField(
        label='Update existing voters',
        help_text='If checked, existing voters will be updated with new data. Otherwise, they will be skipped.',
        required=False,
        initial=False
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']

        allowed = ('.xlsx', '.xls', '.csv')
        if not excel_file.name.lower().endswith(allowed):
            raise forms.ValidationError('Please upload a valid Excel (.xlsx, .xls) or CSV file.')

        if excel_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('File size must be less than 10MB.')

        return excel_file