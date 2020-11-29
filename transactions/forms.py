from django import forms
from django.forms import formset_factory
from .models import (
    Supplier,
    PurchaseBill,
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,
    SaleItem,
    SaleBillDetails
)
from inventory.models import Stock


class SelectSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_deleted=False)
        self.fields['supplier'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = PurchaseBill
        fields = ['supplier']


class PurchaseItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.filter(is_deleted=False)
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update(
            {'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        self.fields['perprice'].widget.attrs.update(
            {'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})

    class Meta:
        model = PurchaseItem
        fields = ['stock', 'quantity', 'perprice']


PurchaseItemFormset = formset_factory(PurchaseItemForm, extra=1)


class PurchaseDetailsForm(forms.ModelForm):
    class Meta:
        model = PurchaseBillDetails
        fields = ['eway', 'veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']


class SupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'textinput form-control', 'pattern': '[a-zA-Z\s]{1,50}', 'title': 'No se permiten numeros'})
        self.fields['phone'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '9', 'pattern': '[0-9]{9}', 'title': 'Solo numeros'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['gstin'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '11', 'pattern': '[A-Z0-9]{11}',
             'title': 'Formato RUC requerido'})

    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'address', 'email', 'gstin']
        widgets = {
            'address': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '4'
                }
            )
        }
        error_messages = {
            'gstin': {
                'unique': "El ruc ingresado ya esta registrado",
            },
            'phone': {
                'unique': 'Ya existe un Proveedor con este telefono'
            }
        }


class SaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'textinput form-control', 'pattern': '[a-zA-Z\s]{1,50}', 'title': 'No se permiten numeros',
             'required': 'true'})
        self.fields['phone'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '9', 'pattern': '[0-9]{9}', 'title': 'Solo números',
             'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['gstin'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '11', 'pattern': '[A-Z0-9]{11}',
             'title': 'Formato RUC requerido'})

    class Meta:
        model = SaleBill
        fields = ['name', 'phone', 'address', 'email', 'gstin']
        widgets = {
            'address': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '4'
                }
            )
        }
        error_messages = {
            'gstin': {
                'unique': "El ruc ingresado ya esta registrado",
            },
            'phone': {
                'unique': 'Ya existe un Proveedor con este telefono'
            }
        }


class SaleItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.filter(is_deleted=False)
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update(
            {'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        self.fields['perprice'].widget.attrs.update(
            {'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})

    class Meta:
        model = SaleItem
        fields = ['stock', 'quantity', 'perprice']


SaleItemFormset = formset_factory(SaleItemForm, extra=1)


class SaleDetailsForm(forms.ModelForm):
    class Meta:
        model = SaleBillDetails
        fields = ['eway', 'veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']
