from django.db import models
class UploadPdf(models.Model):
    imageupload = models.FileField(upload_to='fileupload/', blank=True, null=True)
class User(models.Model):
    file_name = models.CharField(max_length=400)
    seller_name= models.CharField(max_length=400)
    buyer_name = models.CharField(max_length=400)
    gst_no = models.CharField(max_length=400)
    fssai_no = models.CharField(max_length=400)
    invoice_date = models.CharField(max_length=400)
    sr_no = models.CharField(max_length=400)
    item_name = models.CharField(max_length=400)
    hsn_code = models.CharField(max_length=400)
    weight = models.CharField(max_length=400)
    rate= models.CharField(max_length=400)
    amount = models.CharField(max_length=400)
    final_amount = models.CharField(max_length=400)
    description= models.CharField(max_length=400)

class Products(models.Model):
    product_name = models.CharField(max_length=400)

class Brand(models.Model):
    brand_name = models.CharField(max_length=400)















