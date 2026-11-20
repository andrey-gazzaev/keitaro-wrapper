import { memo } from 'react';
import { FetchStreamsButton } from '@/feature/campaign-editor/fetch-streams-button';
import { StreamAdd } from '@/feature/campaign-editor/stream-add';
import { StreamTable } from '@/feature/campaign-editor/stream-table';
import { useCampaignEditor } from '@/feature/campaign-editor/use-campaign-editor';
import { useCampaignTitle } from '@/hooks';
import { PageHead } from '@/ui';

type CampaignEditorProps = {
  /** Keitaro campaign id from the path. */
  readonly campaignId: number;
};

/** Streams, shares, and the controls that change them. */
export const CampaignEditor = memo(function CampaignEditor({ campaignId }: CampaignEditorProps) {
  const editor = useCampaignEditor(campaignId);
  const title = useCampaignTitle(campaignId);

  return (
    <>
      <PageHead
        title={title}
        actions={<FetchStreamsButton pending={editor.fetching} onFetch={editor.fetchStreams} />}
      />

      {editor.loading ? <p className="muted">Загрузка…</p> : null}

      {editor.failed ? <p className="status">Не удалось загрузить потоки.</p> : null}

      <StreamTable
        rows={editor.rows}
        pending={editor.pending}
        onRemove={editor.remove}
        onBringBack={editor.bringBack}
        onBringBackStream={editor.bringBackStream}
        onPin={editor.pin}
        onUnpin={editor.unpin}
        onPush={editor.push}
        onCancel={editor.cancel}
      />

      <StreamAdd targets={editor.targets} adding={editor.adding} onLookup={editor.lookup} onAdd={editor.add} />

      {editor.actionFailed ? <p className="status">Не удалось сохранить правку.</p> : null}
    </>
  );
});
