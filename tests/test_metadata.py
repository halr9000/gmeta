from gallery_vlm.metadata import plan_metadata, TAG_FIELDS

def test_merge_preserves_existing_caption_and_tags():
    meta={'XMP-dc:Description':'old','XMP-dc:Subject':['person'],'XMP-digiKam:TagsList':['person']}
    p=plan_metadata(meta,'new',['person','forest'],skip_existing=False)
    assert p.caption=='old'
    assert p.tags==['person','forest']

def test_overwrite_caption_and_replace_tags():
    p=plan_metadata({'XMP-dc:Description':'old','XMP-dc:Subject':['old']},'new',['new'],skip_existing=False,overwrite_caption=True,replace_tags=True)
    assert p.caption=='new' and p.tags==['new']

def test_skip_existing_is_independent_default_policy():
    p=plan_metadata({'XMP-dc:Description':'old'},'new',['tag'])
    assert p.changed is True and p.caption=='old'
