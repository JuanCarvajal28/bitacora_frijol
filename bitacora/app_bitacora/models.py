from django.db import models
from django.conf import settings

# ==========================
# MODELO: PLANTAS
# ==========================
class Plantas(models.Model):
    id_planta = models.AutoField(primary_key=True)
    nombre_comun = models.CharField(max_length=100)
    nombre_cientifico = models.CharField(max_length=150, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    region_origen = models.CharField(max_length=100, blank=True, null=True)
    edad_planta = models.IntegerField(blank=True, null=True)
    rareza = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='img/')
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plantas'
        verbose_name = "Planta"
        verbose_name_plural = "Plantas"

    def __str__(self):
        return self.nombre_comun

# ==========================
# MODELO: EXPERIMENTOS
# ==========================
class Experimentos(models.Model):
    id_experimento = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, db_column='id_usuario')
    id_planta = models.ForeignKey('Plantas', on_delete=models.DO_NOTHING, db_column='id_planta')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'experimentos'
        verbose_name = "Experimento"
        verbose_name_plural = "Experimentos"

    def __str__(self):
        return self.nombre

# ==========================
# MODELO: REGISTROS
# ==========================
class Registros(models.Model):
    id_registro = models.AutoField(primary_key=True)
    id_experimento = models.ForeignKey(
        Experimentos,
        on_delete=models.DO_NOTHING,
        db_column='id_experimento'
    )
    altura_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)    
    fecha_registro = models.DateField(blank=True, null=True)
    imagen = models.ImageField(upload_to='img/')

    class Meta:
        managed = False
        db_table = 'registros'
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

    def __str__(self):
        return f"Registro {self.id_registro} - Experimento {self.id_experimento_id}"
