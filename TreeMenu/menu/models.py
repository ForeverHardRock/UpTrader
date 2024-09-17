from django.db import models
from slugify import slugify
from django.urls import reverse


class CustomModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Menu(CustomModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название меню")
    url = models.CharField(max_length=200, blank=True, verbose_name="URL", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'меню'
        verbose_name_plural = 'меню'

    def save(self, *args, **kwargs):
        if self.name and not self.url:
            self.url = slugify(str(self.name))
        super(Menu, self).save(*args, **kwargs)


class MenuItem(CustomModel):
    menu = models.ForeignKey(Menu, related_name='items', on_delete=models.CASCADE, verbose_name="Меню")
    title = models.CharField(max_length=100, verbose_name="Название пункта")
    url = models.CharField(max_length=200, blank=True, verbose_name="URL", unique=True)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Родитель")

    class Meta:
        verbose_name = "пункт меню"
        verbose_name_plural = "пункты меню"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title and not self.url:
            self.url = slugify(str(self.title))
        super(MenuItem, self).save(*args, **kwargs)

    def get_url(self):
        parts = []
        current = self
        while current:
            if current.url:
                parts.append(current.url)
            current = current.parent

        parts.reverse()
        url = f"/menu/{self.menu.url}/" + '/'.join(parts) + '/'
        return url
