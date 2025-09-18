include $(E3_REQUIRE_TOOLS)/driver.makefile

APP:=calcApp
APPDB:=$(APP)/Db
APPSRC:=$(APP)/src


USR_INCLUDES += -I$(where_am_I)$(APPSRC)

USR_CFLAGS   += -Wno-unused-variable
USR_CFLAGS   += -Wno-unused-function
USR_CFLAGS   += -Wno-unused-but-set-variable
USR_CPPFLAGS += -Wno-unused-variable
USR_CPPFLAGS += -Wno-unused-function
USR_CPPFLAGS += -Wno-unused-but-set-variable
USR_CPPFLAGS += -DUSE_TYPED_RSET

TEMPLATES += $(wildcard $(APPDB)/*.db)
TEMPLATES += $(wildcard $(APPDB)/*.req)

DBDINC_SRCS += $(APPSRC)/swaitRecord.c
DBDINC_SRCS += $(APPSRC)/sseqRecord.c
DBDINC_SRCS += $(APPSRC)/aCalcoutRecord.c
DBDINC_SRCS += $(APPSRC)/sCalcoutRecord.c
DBDINC_SRCS += $(APPSRC)/transformRecord.c

DBDINC_DBDS = $(subst .c,.dbd,   $(DBDINC_SRCS:$(APPSRC)/%=%))
DBDINC_HDRS = $(subst .c,.h,     $(DBDINC_SRCS:$(APPSRC)/%=%))
DBDINC_DEPS = $(subst .c,$(DEP), $(DBDINC_SRCS:$(APPSRC)/%=%))

HEADERS += $(APPSRC)/sCalcPostfix.h
HEADERS += $(APPSRC)/aCalcPostfix.h
HEADERS += $(DBDINC_HDRS)


SOURCES += $(APPSRC)/sCalcPostfix.c
SOURCES += $(APPSRC)/sCalcPerform.c
SOURCES += $(APPSRC)/aCalcPostfix.c
SOURCES += $(APPSRC)/aCalcPerform.c

SOURCES += $(APPSRC)/calcUtil.c
SOURCES += $(APPSRC)/myFreeListLib.c
SOURCES += $(APPSRC)/devsCalcoutSoft.c
SOURCES += $(APPSRC)/devaCalcoutSoft.c
SOURCES += $(APPSRC)/subAve.c
SOURCES += $(APPSRC)/swaitRecord.c
SOURCES += $(APPSRC)/editSseq.st
SOURCES += $(APPSRC)/interp.c
SOURCES += $(APPSRC)/arrayTest.c
SOURCES += $(APPSRC)/aCalcMonitorMem.c
# DBDINC_SRCS should be last of the series of SOURCES
SOURCES += $(DBDINC_SRCS)

DBDS += $(APPSRC)/calcSupport_LOCAL.dbd
DBDS += $(APPSRC)/calcSupport_withSNCSEQ.dbd
DBDS += $(APPSRC)/calcSupport_withSSCAN.dbd


$(DBDINC_DEPS): $(DBDINC_HDRS)

.dbd.h:
	$(DBTORECORDTYPEH)  $(USR_DBDFLAGS) -o $@ $<
