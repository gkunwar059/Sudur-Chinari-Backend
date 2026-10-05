from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_partner_icon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partner',
            old_name='icon',
            new_name='image',
        ),
    ]
