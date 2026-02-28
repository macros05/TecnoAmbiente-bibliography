import { Routes } from '@angular/router';
import { SearchComponent } from './pages/search/search.component';
import { UploadComponent } from './pages/upload/upload.component';
import { ListPdfsComponent } from './pages/list-pdfs/list-pdfs.component';

export const routes: Routes = [
  { path: 'search', component: SearchComponent,pathMatch: 'full' },
  { path: 'upload', component: UploadComponent },
  { path: 'list-pdfs', component: ListPdfsComponent },

];
