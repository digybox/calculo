from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

# Inventario ampliado con temática Tanta (Comida Peruana)
datos_inventario = {
    1: {"ingrediente": "Lomo Saltado Clásico", "costo_unitario": 6500, "stock_inicial": 80, "ventas_registradas": 0, "stock_real_medido": 80, "limite_tolerancia_porcentaje": 0.05, "imagen": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=500&q=80"},
    2: {"ingrediente": "Ají de Gallina", "costo_unitario": 4500, "stock_inicial": 60, "ventas_registradas": 0, "stock_real_medido": 60, "limite_tolerancia_porcentaje": 0.05, "imagen": "https://images.unsplash.com/photo-1541518763669-27fef04b14ea?w=500&q=80"},
    3: {"ingrediente": "Causa Limeña", "costo_unitario": 3500, "stock_inicial": 40, "ventas_registradas": 0, "stock_real_medido": 40, "limite_tolerancia_porcentaje": 0.05, "imagen": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=500&q=80"},
    4: {"ingrediente": "Pisco Sour", "costo_unitario": 3000, "stock_inicial": 100, "ventas_registradas": 0, "stock_real_medido": 100, "limite_tolerancia_porcentaje": 0.05, "imagen": "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=500&q=80"},
    5: {"ingrediente": "Suspiro a la Limeña", "costo_unitario": 2500, "stock_inicial": 50, "ventas_registradas": 0, "stock_real_medido": 50, "limite_tolerancia_porcentaje": 0.05, "imagen": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&q=80"}
}

def vista_cliente(request):
    if request.method == 'POST':
        item_id = int(request.POST.get('item_id'))
        if item_id in datos_inventario:
            datos_inventario[item_id]['ventas_registradas'] += 1
        return redirect('cliente')
    return render(request, 'inventario/cliente.html', {'menu': datos_inventario.items()})

# Vistas de Autenticación
def registro_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Inicia sesión automáticamente tras registro
            return redirect('cliente')
    else:
        form = UserCreationForm()
    return render(request, 'inventario/registro.html', {'form': form})

def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('dashboard')
            return redirect('cliente')
    else:
        form = AuthenticationForm()
    return render(request, 'inventario/login.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('cliente')

# Función para verificar si el usuario es staff (Administrador/Trabajador)
def es_admin(user):
    return user.is_staff

# Protegemos el dashboard: Solo usuarios logueados que sean "staff" pueden entrar
@login_required(login_url='login')
@user_passes_test(es_admin, login_url='cliente')
def dashboard_admin(request):
    if request.method == 'POST':
        item_id = int(request.POST.get('item_id'))
        nuevo_stock = int(request.POST.get('nuevo_stock'))
        if item_id in datos_inventario:
            datos_inventario[item_id]['stock_real_medido'] = nuevo_stock
        return redirect('dashboard')

    reporte_mermas = []
    nombres_ingredientes = []
    stocks_teoricos = []
    stocks_reales = []

    for id, item in datos_inventario.items():
        stock_teorico = item["stock_inicial"] - item["ventas_registradas"]
        delta_i = item["stock_real_medido"] - stock_teorico
        limite_L = item["stock_inicial"] * item["limite_tolerancia_porcentaje"]
        
        alerta = False
        estado = "Normal"
        if abs(delta_i) > limite_L:
            alerta = True
            estado = "Alerta: Merma" if delta_i < 0 else "Alerta: Sobrestock"
            
        impacto_financiero = abs(delta_i) * item["costo_unitario"]

        reporte_mermas.append({
            "id": id, "ingrediente": item["ingrediente"], "stock_inicial": item["stock_inicial"],
            "ventas": item["ventas_registradas"], "stock_teorico": stock_teorico,
            "stock_real": item["stock_real_medido"], "delta_i": delta_i, "limite_L": limite_L,
            "alerta": alerta, "estado": estado, "impacto": impacto_financiero
        })
        nombres_ingredientes.append(item["ingrediente"])
        stocks_teoricos.append(stock_teorico)
        stocks_reales.append(item["stock_real_medido"])

    contexto = {'reporte': reporte_mermas, 'nombres': nombres_ingredientes, 'teoricos': stocks_teoricos, 'reales': stocks_reales}
    return render(request, 'inventario/dashboard.html', contexto)