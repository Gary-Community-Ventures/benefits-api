from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("screener", "0090_merge_20241213_1726"),
    ]

    operations = [
        migrations.AddField(
            model_name="screen",
            name="has_nccip",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
