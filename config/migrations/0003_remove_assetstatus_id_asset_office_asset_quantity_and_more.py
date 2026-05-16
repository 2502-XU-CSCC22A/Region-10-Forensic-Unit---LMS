import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_alter_asset_date_acquired'),
    ]

    operations = [
       
        migrations.AddField(
            model_name='asset',
            name='office',
            field=models.CharField(blank=True, db_column='Office', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='assetstatus',
            name='status_id',
            field=models.AutoField(db_column='StatusID', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='asset',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to='config.category'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='assetstatus',
            name='status_name',
            field=models.CharField(db_column='Status_Name', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterModelTable(
            name='asset',
            table='config_asset',
        ),
    ]
