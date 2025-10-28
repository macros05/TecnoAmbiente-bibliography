import { Component } from '@angular/core';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { DocumentoService } from '../../services/documentos.service';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from '../../../material/material.module';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule, MaterialModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  archivos: File[] = [];
  procesadosCorrectamente: string[] = [];
  erroresProcesamiento: { archivo: string; error: string }[] = [];
  cargando: boolean = false;
  progreso: number = 0; 

  constructor(private documentoService: DocumentoService) { }

  onArchivosSeleccionados(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input?.files?.length) {
      this.archivos = Array.from(input.files);
    }
  }

  subirPDFs() {
      const totalSize = this.archivos.reduce((acc, f) => acc + f.size, 0);

    if (this.archivos.length === 0) {
      alert('Por favor, selecciona al menos un archivo.');
      return;
    }
    if (totalSize > 200 * 1024 * 1024) {
      alert('Has seleccionado más de 1000MB. Por favor, sube en varias tandas.');
      return;
    }
    this.cargando = true;
    this.progreso = 0;

    this.documentoService.subirDocumentosConProgreso(this.archivos).subscribe({
      next: (event: HttpEvent<any>) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.progreso = Math.round(100 * event.loaded / event.total);
        } else if (event.type === HttpEventType.Response) {
          this.cargando = false;
          this.procesadosCorrectamente = [];
          this.erroresProcesamiento = [];

          event.body.resultados.forEach((r: any) => {
            if (r.status.includes('✅')) {
              this.procesadosCorrectamente.push(r.archivo);
            } else {
              this.erroresProcesamiento.push({ archivo: r.archivo, error: r.error });
            }
          });

          this.archivos = []; // limpiar tras subida
        }
      },
      error: (err: any) => {
        this.cargando = false;
        console.error('Error al subir:', err);
        alert('Error general al subir los documentos');
      }
    });
  }
}
