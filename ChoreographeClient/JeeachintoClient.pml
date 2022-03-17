<?xml version="1.0" encoding="UTF-8" ?>
<Package name="JeeachintoClient" format_version="5">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="__init__" src="behavior_1/lib/jeeachinto/__init__.py" />
        <File name="client" src="behavior_1/lib/jeeachinto/client.py" />
        <File name="server" src="behavior_1/lib/jeeachinto/server.py" />
        <File name="utils" src="behavior_1/lib/jeeachinto/utils.py" />
    </Resources>
    <Topics />
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
        <Translation name="translation_it_IT" src="translations/translation_it_IT.ts" language="it_IT" />
    </Translations>
</Package>
