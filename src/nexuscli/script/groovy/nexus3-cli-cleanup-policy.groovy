// Original from:
// https://github.com/idealista/nexus-role/blob/master/files/scripts/cleanup_policy.groovy
import groovy.json.JsonSlurper
import groovy.json.JsonBuilder
import java.util.concurrent.TimeUnit

import org.sonatype.nexus.cleanup.storage.CleanupPolicy
import org.sonatype.nexus.cleanup.storage.CleanupPolicyStorage
import com.google.common.collect.Maps

import static org.sonatype.nexus.repository.search.DefaultComponentMetadataProducer.IS_PRERELEASE_KEY
import static org.sonatype.nexus.repository.search.DefaultComponentMetadataProducer.LAST_BLOB_UPDATED_KEY
import static org.sonatype.nexus.repository.search.DefaultComponentMetadataProducer.LAST_DOWNLOADED_KEY


def cleanupPolicyStorage = container.lookup(CleanupPolicyStorage.class.getName())

parsed_args = new JsonSlurper().parseText(args)
parsed_args.each {
    log.debug("Received arguments: <${it.key}=${it.value}> (${it.value.getClass()})")
}

if (parsed_args.name == null) {
    throw new Exception("Missing mandatory argument: name")
}

// "get" operation
if (parsed_args.size() == 1) {
    existingPolicy = cleanupPolicyStorage.get(parsed_args.name)
    return toJsonString(existingPolicy)
}

// create and update use this
Map<String, String> criteriaMap = createCriteria(parsed_args)

// "update" operation
if (cleanupPolicyStorage.exists(parsed_args.name)) {
    existingPolicy = cleanupPolicyStorage.get(parsed_args.name)
    existingPolicy.setNotes(parsed_args.notes)
    existingPolicy.setCriteria(criteriaMap)
    cleanupPolicyStorage.update(existingPolicy)
    return toJsonString(existingPolicy)
}

// "create" operation
format = parsed_args.format == "all" ? "ALL_FORMATS" : parsed_args.format
cleanupPolicy = new CleanupPolicy(
        name: parsed_args.name,
        notes: parsed_args.notes,
        format: format,
        mode: 'deletion',
        criteria: criteriaMap
)
cleanupPolicyStorage.add(cleanupPolicy)
return toJsonString(cleanupPolicy)


def Map<String, String> createCriteria(parsed_args) {
    Map<String, String> criteriaMap = Maps.newHashMap()
    if (parsed_args.published_before == null) {
        criteriaMap.remove(LAST_BLOB_UPDATED_KEY)
    } else {
        criteriaMap.put(LAST_BLOB_UPDATED_KEY, asStringSeconds(parsed_args.published_before))
    }
    if (parsed_args.last_download_before == null) {
        criteriaMap.remove(LAST_DOWNLOADED_KEY)
    } else {
        criteriaMap.put(LAST_DOWNLOADED_KEY, asStringSeconds(parsed_args.last_download_before))
    }
    if (parsed_args.is_pre_release != "") {
        criteriaMap.put(IS_PRERELEASE_KEY, String.valueOf(parsed_args.is_pre_release))
    }
    return criteriaMap
}

def Integer asSeconds(days) {
    return days * TimeUnit.DAYS.toSeconds(1)
}

def String asStringSeconds(daysInt) {
    return String.valueOf(asSeconds(daysInt))
}

// There's got to be a better way to do this.
// using JsonOutput directly on the object causes a stack overflow
def String toJsonString(cleanup_policy) {
    def policyString = new JsonBuilder()
    policyString {
        name cleanup_policy.getName()
        notes cleanup_policy.getNotes()
        format cleanup_policy.getFormat()
        mode cleanup_policy.getMode()
        criteria cleanup_policy.getCriteria()
    }
    return policyString.toPrettyString()
}
