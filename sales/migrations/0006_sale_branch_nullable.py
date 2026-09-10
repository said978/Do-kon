from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_branch_address_remove_branch_created_at_and_more'),
        ('sales', '0005_alter_customer_options_alter_debtpayment_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='branch',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='accounts.branch',
                verbose_name='Filial',
            ),
        ),
    ]
