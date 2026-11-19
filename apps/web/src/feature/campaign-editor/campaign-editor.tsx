import { Stack } from '@/ui';
import { FetchStreams } from './fetch-streams';
import { StreamAdd } from './stream-add';
import { StreamTable } from './stream-table';
import { useCampaignEditor } from './use-campaign-editor';

type CampaignEditorProps = {
  /** Keitaro campaign id from the path. */
  readonly campaignId: number;
};

/** Streams, shares, and the controls that change them. */
export function CampaignEditor({ campaignId }: CampaignEditorProps) {
  const editor = useCampaignEditor(campaignId);

  return (
    <Stack as="section" variant="start">
      <FetchStreams pending={editor.fetching} onFetch={editor.fetchStreams} />

      {editor.loading ? <p className="muted">Загрузка…</p> : null}

      {editor.failed ? <p className="status">Не удалось загрузить потоки.</p> : null}

      <StreamTable
        rows={editor.rows}
        onRemove={editor.remove}
        onBringBack={editor.bringBack}
        onPin={editor.pin}
        onUnpin={editor.unpin}
        onPush={editor.push}
        onCancel={editor.cancel}
      />

      <StreamAdd targets={editor.targets} onLookup={editor.lookup} onAdd={editor.add} />

      {editor.actionFailed ? <p className="status">Не удалось сохранить правку.</p> : null}
    </Stack>
  );
}
