from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    PurchaseBill,
    Supplier,
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,
    SaleItem,
    SaleBillDetails
)
from .forms import (
    SelectSupplierForm,
    PurchaseItemFormset,
    PurchaseDetailsForm,
    SupplierForm,
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm
)
from inventory.models import Stock


# muestra la lista de proveedores
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False)
    paginate_by = 10


# agregar proveedor
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Proveedor agregado correctamente"
    template_name = "suppliers/edit_supplier.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Agregar Proveedor'
        context["savebtn"] = 'Agregar Proveedor'
        return context


# actualizar proveedor
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "El proveedor fue actualizado correctamente"
    template_name = "suppliers/edit_supplier.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Editar Proveedor'
        context["savebtn"] = 'Guardar Cambios'
        context["delbtn"] = 'Delete Supplier'
        return context


# eliminar proveedor
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "El proveedor fue eliminado correctamente"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object': supplier})

    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()
        messages.success(request, self.success_message)
        return redirect('suppliers-list')


# detalle de proveedor
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier': supplierobj,
            'bills': bills
        }
        return render(request, 'suppliers/supplier.html', context)


# muestra las compras
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


# detalle de compra
class SelectSupplierView(View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("supplier")
            supplier = get_object_or_404(Supplier, id=supplierid)
            return redirect('new-purchase', supplier.pk)
        return render(request, self.template_name, {'form': form})


# nueva compra
class PurchaseCreateView(View):
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        formset = PurchaseItemFormset(request.GET or None)
        supplierobj = get_object_or_404(Supplier, pk=pk)
        context = {
            'formset': formset,
            'supplier': supplierobj,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST)
        supplierobj = get_object_or_404(Supplier, pk=pk)
        if formset.is_valid():

            billobj = PurchaseBill(
                supplier=supplierobj)
            billobj.save()

            billdetailsobj = PurchaseBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:
                billitem = form.save(commit=False)
                billitem.billno = billobj

                stock = get_object_or_404(Stock, name=billitem.stock.name)

                billitem.totalprice = billitem.perprice * billitem.quantity

                stock.quantity += billitem.quantity

                stock.save()
                billitem.save()
            messages.success(request, "Compra registrada correctamente")
            return redirect('purchase-bill', billno=billobj.billno)
        formset = PurchaseItemFormset(request.GET or None)
        context = {
            'formset': formset,
            'supplier': supplierobj
        }
        return render(request, self.template_name, context)


# eliminar compra
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transactions/purchases'

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Compra eliminada correctamente")
        return super(PurchaseDeleteView, self).delete(*args, **kwargs)


# lista de ventas
class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


# nueva venta
class SaleCreateView(View):
    template_name = 'sales/new_sale.html'

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form': form,
            'formset': formset,
            'stocks': stocks
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)
        if form.is_valid() and formset.is_valid():

            billobj = form.save(commit=False)
            billobj.save()

            billdetailsobj = SaleBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:
                billitem = form.save(commit=False)
                billitem.billno = billobj

                stock = get_object_or_404(Stock, name=billitem.stock.name)

                billitem.totalprice = billitem.perprice * billitem.quantity

                stock.quantity -= billitem.quantity

                stock.save()
                billitem.save()
            messages.success(request, "Venta registrada correctamente")
            return redirect('sale-bill', billno=billobj.billno)
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'form': form,
            'formset': formset,
        }
        return render(request, self.template_name, context)


# eliminar venta
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Venta eliminada correctamente")
        return super(SaleDeleteView, self).delete(*args, **kwargs)


# detalle de compra
class PurchaseBillView(View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill': PurchaseBill.objects.get(billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno),
            'billdetails': PurchaseBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = PurchaseBillDetails.objects.get(billno=billno)

            billdetailsobj.eway = request.POST.get("eway")
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Los detalles de compra se han actualizado correctamente")
        context = {
            'bill': PurchaseBill.objects.get(billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno),
            'billdetails': PurchaseBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)


# detalle de venta
class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill': SaleBill.objects.get(billno=billno),
            'items': SaleItem.objects.filter(billno=billno),
            'billdetails': SaleBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = SaleBillDetails.objects.get(billno=billno)

            billdetailsobj.eway = request.POST.get("eway")
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Los detalles de venta se han actualizado correctamente")
        context = {
            'bill': SaleBill.objects.get(billno=billno),
            'items': SaleItem.objects.filter(billno=billno),
            'billdetails': SaleBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)
