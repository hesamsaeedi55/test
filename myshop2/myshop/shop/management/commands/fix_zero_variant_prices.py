"""
Django management command to fix variants with 0 price by setting them to product base price
Usage: python manage.py fix_zero_variant_prices
"""
from django.core.management.base import BaseCommand
from shop.models import ProductVariant


class Command(BaseCommand):
    help = 'Fix variants that have price_toman = 0 by setting them to their product\'s base price'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 DRY RUN MODE - No changes will be made'))
            self.stdout.write('')
        
        self.stdout.write('🔍 Finding variants with price_toman = 0...')
        
        # Find all variants with 0 price
        zero_price_variants = ProductVariant.objects.filter(
            price_toman=0, 
            is_active=True
        ).select_related('product')
        
        count = zero_price_variants.count()
        self.stdout.write(f'Found {count} variants with 0 price')
        self.stdout.write('')
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No variants found with 0 price. All good!'))
            return
        
        updated_count = 0
        skipped_count = 0
        
        for variant in zero_price_variants:
            product = variant.product
            product_price = product.price_toman
            
            self.stdout.write(f'Variant ID {variant.id}: {variant.sku}')
            self.stdout.write(f'  Product: {product.name} (ID: {product.id})')
            self.stdout.write(f'  Product price: {product_price} تومان')
            self.stdout.write(f'  Current variant price: {variant.price_toman} تومان')
            self.stdout.write(f'  Attributes: {variant.attributes}')
            
            if product_price and product_price > 0:
                if not dry_run:
                    variant.price_toman = product_price
                    variant.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Updated to {product_price} تومان'))
                else:
                    self.stdout.write(self.style.WARNING(f'  🧪 Would update to {product_price} تومان'))
                updated_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Skipped (product price is also 0 or invalid)'))
                skipped_count += 1
            
            self.stdout.write('')
        
        self.stdout.write('='*50)
        if dry_run:
            self.stdout.write(self.style.WARNING(f'🧪 Would update {updated_count} variants'))
            self.stdout.write(self.style.WARNING(f'⚠️  Would skip {skipped_count} variants'))
            self.stdout.write('')
            self.stdout.write('Run without --dry-run to apply changes')
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_count} variants'))
            self.stdout.write(self.style.WARNING(f'⚠️  Skipped {skipped_count} variants (product price also 0)'))

