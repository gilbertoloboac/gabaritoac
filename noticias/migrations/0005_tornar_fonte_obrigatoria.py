from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0004_alter_noticiapage_fonte_original_url_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="noticiapage",
            name="fonte",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="noticias.fontesnippet",
                verbose_name="Fonte",
            ),
        ),
    ]
