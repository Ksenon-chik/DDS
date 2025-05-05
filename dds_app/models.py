from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name


class Type(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        unique_together = ('name', 'type')

    def __str__(self): return f"{self.name} ({self.type})"


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        unique_together = ('name', 'category')

    def __str__(self): return f"{self.name} ({self.category})"


class Transaction(models.Model):
    created_at = models.DateField(auto_now_add=True)
    date = models.DateField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, related_name='transactions')
    type = models.ForeignKey(Type, on_delete=models.PROTECT, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} | {self.type} | {self.amount}"
