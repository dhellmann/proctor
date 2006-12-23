#
# $Id$
#

#
# 0. (tag work directory)
# 1. gmake dist REV=rX_Y
# 2. gmake ftp_install REV=rX_Y
# 3. (create new release, add file)
#

PRODUCT_NAME=Proctor

FTP_SERVER="upload.sourceforge.net"
FTP_DEST_DIR="/incoming"
FTP_USER="anonymous"

SSH_USER="doughellmann"
SSH_SERVER="proctor.sourceforge.net"
SSH_DEST_DIR="/home/groups/p/pr/proctor/htdocs"
SSH_DOCS_DEST_DIR="/home/groups/p/pr/proctor/htdocs"

ifeq ($(TEST_SET),)
TEST_SET="all"
endif

REGRESSION_ROOT_DIR=$(CWD)/../ProctorRegressionTest
REGRESSION_RUN_DIR=$(REGRESSION_ROOT_DIR)/Run
REGRESSION_BASELINE_DIR=$(REGRESSION_ROOT_DIR)/RegressionBaseline

#REGRESSION_TEST=echo "Cleaning up..."; rm -rf $(REGRESSION_RUN_DIR); echo "Starting test..."; ./test_happydoc.py -d $(REGRESSION_RUN_DIR)  $(TEST_SET) | tee $(REGRESSION_ROOT_DIR)/run_trace.txt; mv $(REGRESSION_ROOT_DIR)/run_trace.txt $(REGRESSION_RUN_DIR)/trace.txt

REGRESSION_TEST_ESTABLISH_BASELINE=(cd $(REGRESSION_BASELINE_DIR); rm -rf *); cd $(REGRESSION_RUN_DIR); tar cf - * | (cd $(REGRESSION_BASELINE_DIR); tar xf -)

REGRESSION_TEST_COMPARE_RESULTS=echo ; echo "Comparing current run to baseline..." ; diff -r $(REGRESSION_BASELINE_DIR) $(REGRESSION_RUN_DIR) 2>&1 > $(REGRESSION_ROOT_DIR)/regression_test_differences.txt

REGRESSION_TEST_FAIL_MESSAGE="See $(REGRESSION_ROOT_DIR)/regression_test_differences.txt, `wc -l $(REGRESSION_ROOT_DIR)/regression_test_differences.txt | awk '{print $$1}'` lines different"

include Package.mak

tags:
	find . -name '*.py' | etags -l auto --regex='/[ \t]*\def[ \t]+\([^ :(\t]+\)/\1/' -
