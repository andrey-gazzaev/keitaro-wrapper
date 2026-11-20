import type { StreamEditor, StreamGroup, StreamLine } from '@/models';
import type { CampaignEditorVm, StreamRowVm } from '@/view-models';

/** Table and add targets for one editor. Empty before the first fetch. */
export function mapCampaignEditor(editor: StreamEditor | undefined): CampaignEditorVm {
  const rows = (editor?.streams ?? []).flatMap(mapStreamRows);

  return {
    table: { rows },
    targets: rows.filter((row) => row.selectable),
  };
}

function mapStreamRows(stream: StreamGroup): StreamRowVm[] {
  const header = mapHeader(stream);

  if (stream.lines.length === 0) {
    return [header];
  }

  return [header, ...stream.lines.map((line) => mapLine(stream, line))];
}

function mapHeader(stream: StreamGroup): StreamRowVm {
  return {
    key: `stream-${stream.id}`,
    flow: stream.name,
    share: '',
    pinned: false,
    deleted: stream.deleted,
    dirty: stream.dirty,
    header: true,
    selectable: stream.acceptsOffers,
    bringBack: stream.deleted,
    remove: false,
    pin: false,
    publish: stream.dirty && !stream.deleted,
    bindingId: 0,
    streamId: stream.id,
  };
}

function mapLine(stream: StreamGroup, line: StreamLine): StreamRowVm {
  const live = !line.deleted && !stream.deleted;

  return {
    key: `line-${line.id}`,
    flow: line.name,
    share: line.share,
    pinned: line.pinned,
    deleted: line.deleted,
    dirty: stream.dirty,
    header: false,
    selectable: false,
    bringBack: line.deleted && !stream.deleted,
    remove: live,
    pin: live,
    publish: false,
    bindingId: line.id,
    streamId: stream.id,
  };
}
