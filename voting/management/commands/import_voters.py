import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from voting.models import Voter
import os


class Command(BaseCommand):
    help = 'Import voters from Excel or CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the Excel (.xlsx, .xls) or CSV file'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing voters'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default=0,
            help='Sheet name or index (default: 0 - first sheet)'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        overwrite = options['overwrite']
        sheet = options['sheet']

        # Check if file exists
        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist')

        try:
            # Read file based on extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            self.stdout.write(self.style.WARNING(f'Reading file: {file_path}...'))
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                # Try with openpyxl first, fallback to xlrd for .xls
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
                except:
                    df = pd.read_excel(file_path, sheet_name=sheet, engine='xlrd')
            else:
                raise CommandError(f'Unsupported file format: {file_ext}. Use .xlsx, .xls, or .csv')

            # Validate required columns
            required_columns = ['voter_no', 'name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise CommandError(f'Missing required columns: {", ".join(missing_columns)}')

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

            created_count = 0
            updated_count = 0
            skipped_count = 0
            errors = []

            self.stdout.write(self.style.WARNING(f'Processing {len(df)} rows...'))

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

                        # Get or create voter
                        voter, created = Voter.objects.get_or_create(
                            voter_no=voter_no,
                            defaults={'name': name, 'house': house}
                        )

                        if created:
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Created: {voter_no} - {name}')
                            )
                        elif overwrite:
                            voter.name = name
                            voter.house = house
                            voter.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'↻ Updated: {voter_no} - {name}')
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'⊘ Skipped: {voter_no} (already exists)')
                            )

                    except Exception as e:
                        errors.append(f"Row {index + 2}: {str(e)}")
                        skipped_count += 1

            # Summary
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {created_count}'))
            if overwrite:
                self.stdout.write(self.style.WARNING(f'↻ Updated: {updated_count}'))
            self.stdout.write(self.style.WARNING(f'⊘ Skipped: {skipped_count}'))
            
            if errors:
                self.stdout.write(self.style.ERROR(f'\n✗ Errors ({len(errors)}):'))
                for error in errors[:10]:
                    self.stdout.write(self.style.ERROR(f'  • {error}'))
                if len(errors) > 10:
                    self.stdout.write(self.style.ERROR(f'  ... and {len(errors) - 10} more errors'))

            self.stdout.write('=' * 60)
            self.stdout.write(self.style.SUCCESS(f'\n✓ Import completed successfully!'))

        except Exception as e:
            raise CommandError(f'Error processing file: {str(e)}')