import { openDialog } from 'vue3-promise-dialog';
import ConfirmDialog from '@/components/ConfirmDialog.vue';

export async function confirm(text: string) {
  return await openDialog(ConfirmDialog, {text});
}
