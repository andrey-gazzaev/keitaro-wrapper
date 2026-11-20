import { Button } from '@/ui';
import styles from './create-campaign-actions.module.css';

type CreateCampaignActionsProps = {
  /** True while the create is in flight. */
  readonly pending: boolean;

  /** Closes the dialog. */
  readonly onClose: () => void;
};

/** Cancel and create controls. */
export function CreateCampaignActions({ pending, onClose }: CreateCampaignActionsProps) {
  return (
    <div className={styles.actions}>
      <Button type="button" variant="secondary" onClick={onClose}>
        Отмена
      </Button>
      <Button type="submit" variant="primary" pending={pending}>
        Создать
      </Button>
    </div>
  );
}
