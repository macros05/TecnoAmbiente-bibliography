import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth/services/auth.service';
import { MaterialModule } from '../material/material.module';

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css'],
  imports: [MaterialModule, RouterModule]
})
export class LayoutComponent implements OnInit {
  public sidebarItems = [
    { label: 'Buscar documentos', icon: 'search', url: '/search' },
    { label: 'Subir PDF', icon: 'upload_file', url: '/upload' },
    { label: 'Listar PDFs', icon: 'picture_as_pdf', url: '/list-pdfs' },
    { label: 'Admin / Ajustes', icon: 'settings', url: '/admin', role: 'admin' }  
  ];

  public userName: string = '';
  public userRole: string = ''; // Para almacenar el rol del usuario

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.userName = this.authService.getUserName(); // Obtener el nombre de usuario del token
    this.userRole = this.authService.getUserRole(); // Obtener el rol del usuario
    this.filterSidebarItems(); // Filtrar los items del sidebar según el rol
  }

  // Filtra los items del sidebar dependiendo del rol
  filterSidebarItems(): void {
    if (this.userRole !== 'admin') {
      this.sidebarItems = this.sidebarItems.filter(item => item.role !== 'admin');
    }
  }

  // Función de logout
  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']); // Redirige al login
  }
}
