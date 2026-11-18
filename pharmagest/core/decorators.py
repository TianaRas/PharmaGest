from django.contrib.auth.decorators import user_passes_test

def est_admin(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

def est_pharmacien_ou_admin(user):
    return user.is_authenticated and user.role in ('ADMIN', 'PHARMACIEN')

def peut_vendre(user):
    return user.is_authenticated and user.role in ('ADMIN', 'CAISSIER', 'PHARMACIEN')

def peut_gerer_stock(user):
    return user.is_authenticated and user.role in ('ADMIN', 'GESTIONNAIRE_STOCK', 'PHARMACIEN')

def peut_voir_rapports(user):
    return user.is_authenticated and user.role in ('ADMIN', 'RESPONSABLE_GESTION', 'PHARMACIEN')

# Décorateurs prêts à l'emploi (sans raise_exception)
admin_requis = user_passes_test(est_admin, login_url='utilisateurs:login')
pharmacien_requis = user_passes_test(est_pharmacien_ou_admin, login_url='utilisateurs:login')
vente_requise = user_passes_test(peut_vendre, login_url='utilisateurs:login')
stock_requis = user_passes_test(peut_gerer_stock, login_url='utilisateurs:login')
rapports_requis = user_passes_test(peut_voir_rapports, login_url='utilisateurs:login')