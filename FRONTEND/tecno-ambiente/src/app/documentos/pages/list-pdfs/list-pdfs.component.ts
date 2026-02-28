import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; // Importante para *ngIf, *ngFor
import { FormsModule } from '@angular/forms';     // Importante para [(ngModel)]
import { RouterModule } from '@angular/router';

import { Documento } from '../../interfaces/document.interface';
import { DocumentoService } from '../../services/documentos.service'; 
import { MaterialModule } from '../../../material/material.module';

import Swal from 'sweetalert2'; 

@Component({
  selector: 'app-list-pdfs',
  standalone: true,
  imports: [CommonModule, FormsModule, MaterialModule, RouterModule], 
  templateUrl: './list-pdfs.component.html',
  styleUrls: ['./list-pdfs.component.css']
})
export class ListPdfsComponent implements OnInit {

  // --- DATOS ---
  documentos: Documento[] = [];
  
  // --- PAGINACIÓN Y ESTADO ---
  totalRegistros = 0;
  paginaActual = 1;
  pageSize = 10;
  totalPages = 0;
  cargando = false;

  // --- FILTROS ---
  filtroTitulo = '';

  // --- ORDENACIÓN (NUEVO) ---
  columnaOrdenada: string = '';       // '' | 'titulo' | 'fecha'
  ordenDireccion: 'asc' | 'desc' = 'asc';

  constructor(private docService: DocumentoService) {}

  ngOnInit(): void {
    this.cargarDocumentos();
  }

  // ==========================================
  // 1. CARGA DE DATOS
  // ==========================================
  cargarDocumentos() {
    this.cargando = true;

    this.docService.buscarPorFiltros({
      titulo: this.filtroTitulo,
      page: this.paginaActual,
      page_size: this.pageSize,
      order_by: this.columnaOrdenada,
      order_dir: this.ordenDireccion
    }).subscribe({
      next: (resp) => {
        this.documentos = resp.resultados;
        this.totalRegistros = resp.total;
        this.totalPages = Math.ceil(this.totalRegistros / this.pageSize);
        

        this.cargando = false;
      },
      error: (err) => {
        console.error('Error cargando lista', err);
        this.cargando = false;
        
        const Toast = Swal.mixin({
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 3000
        });
        Toast.fire({
          icon: 'error',
          title: 'Error al cargar los documentos'
        });
      }
    });
  }

  ordenar(columna: string) {
    // 1. Cambias las variables de dirección igual que antes
    if (this.columnaOrdenada === columna) {
      this.ordenDireccion = this.ordenDireccion === 'asc' ? 'desc' : 'asc';
    } else {
      this.columnaOrdenada = columna;
      this.ordenDireccion = 'asc';
    }

    // 2. EN LUGAR DE ORDENAR A MANO AQUÍ...
    // ¡Recargamos los datos desde el servidor con el nuevo orden!
    this.cargarDocumentos(); 
}
  // ==========================================
  // 3. PAGINACIÓN Y BÚSQUEDA
  // ==========================================
  cambiarPagina(delta: number) {
    const nuevaPagina = this.paginaActual + delta;
    if (nuevaPagina >= 1 && nuevaPagina <= this.totalPages) {
      this.paginaActual = nuevaPagina;
      this.cargarDocumentos();
    }
  }

  buscar() {
    this.paginaActual = 1;
    this.cargarDocumentos();
  }

  // ==========================================
  // 4. ACCIONES (VER / ELIMINAR)
  // ==========================================
  abrirPdf(rutaPdf: string) {
    const nombreArchivo = rutaPdf.split('/').pop() || rutaPdf;
    this.cargando = true;

    this.docService.verPdf(nombreArchivo).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error descargando PDF', err);
        this.cargando = false;
        
        Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: 'No se pudo abrir el PDF. Verifica que el archivo existe en el servidor.',
          confirmButtonColor: '#d33'
        });
      }
    });
  }

  eliminar(doc: Documento) {
    Swal.fire({
      title: '¿Estás seguro?',
      text: `Vas a eliminar el documento "${doc.titulo}". Esta acción no se puede deshacer.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      
      if (result.isConfirmed) {
        this.cargando = true; 
        
        this.docService.eliminarDocumento(doc.id).subscribe({
          next: () => {
            // Eliminamos visualmente de la lista actual
            this.documentos = this.documentos.filter(d => d.id !== doc.id);
            this.totalRegistros--;
            this.cargando = false;

            Swal.fire(
              '¡Eliminado!',
              'El documento ha sido borrado correctamente.',
              'success'
            );
          },
          error: (err) => {
            console.error(err);
            this.cargando = false;

            Swal.fire(
              'Error',
              'Hubo un problema al eliminar el documento.',
              'error'
            );
          }
        });
      }
    });
  }

  // Helper para template
  getKeywordsArray(texto: string): string[] {
    if (!texto) return [];
    return texto.split(',').slice(0, 3);
  }
}