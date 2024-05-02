from django.shortcuts import redirect


def redirect_by_role(user):
    role = user
    if role == 'administrator':
        return redirect('admin_dashboard')
    elif role == 'accountant':
        return redirect('accountant_dashboard')
    elif role == 'employee':
        return redirect('employees:certificaciones')
    elif role == 'entrepreneur':
        return redirect('companies:index_companies')
    else:
        return redirect('error_page')