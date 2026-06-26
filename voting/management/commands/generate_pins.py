import os
import random
import string
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from voting.models import Voter

class Command(BaseCommand):
    help = 'Generate PINs for voters and export the complete list to an Excel file.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing PINs for all voters',
        )
        parser.add_argument(
            '-o', '--output',
            type=str,
            default='voter_pins.xlsx',
            help='Output file path for the Excel sheet (default: voter_pins.xlsx)',
        )

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        output_path = options['output']

        # Determine which voters need PINs
        if overwrite:
            voters_to_update = Voter.objects.all()
            self.stdout.write('Generating/overwriting PINs for ALL voters...')
        else:
            voters_to_update = Voter.objects.filter(Q(pin__isnull=True) | Q(pin=''))
            self.stdout.write('Generating PINs for voters without a PIN...')

        count = voters_to_update.count()
        if count > 0:
            with transaction.atomic():
                voters_list = list(voters_to_update)
                for voter in voters_list:
                    voter.pin = "".join(random.choices(string.digits, k=6))
                
                Voter.objects.bulk_update(voters_list, ['pin'])
            self.stdout.write(self.style.SUCCESS(f'Successfully generated PINs for {count} voters.'))
        else:
            self.stdout.write(self.style.WARNING('No voters needed new PINs.'))

        # Now export ALL voters to Excel using values() to prevent model instantiation and minimize memory usage
        voters_data = Voter.objects.values('voter_no', 'full_name', 'house', 'pin').order_by('full_name')
        if not voters_data.exists():
            self.stdout.write(self.style.WARNING('No voters found in database to export.'))
            return

        self.stdout.write(f'Exporting all voters to {output_path}...')

        # Construct DataFrame directly from the list of dictionaries
        df = pd.DataFrame(list(voters_data))
        # Ensure column order matches expectation
        df = df[['voter_no', 'full_name', 'house', 'pin']]

        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Voter PINs')

                workbook = writer.book
                worksheet = writer.sheets['Voter PINs']
                from openpyxl.styles import Font, PatternFill
                header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
                header_font = Font(bold=True)

                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font

                worksheet.column_dimensions['A'].width = 15
                worksheet.column_dimensions['B'].width = 30
                worksheet.column_dimensions['C'].width = 20
                worksheet.column_dimensions['D'].width = 15

            self.stdout.write(self.style.SUCCESS(f'Successfully exported list to {output_path}'))
        except Exception as e:
            raise CommandError(f'Failed to write Excel file: {e}')
