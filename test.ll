
%struct.str = type {i32}

define void @func.quicksort(%struct.str* %s.ptr, i32 %left, i32 %right) {
    %left.ptr = alloca i32
    %right.ptr = alloca i32
    store i32 %left, i32* %left.ptr
    store i32 %right, i32* %right.ptr
    %i.ptr = alloca i32
    %left.1 = load i32, i32* %left.ptr
    store i32 %left.1, i32* %i.ptr
    %j.ptr = alloca i32
    %right.2 = load i32, i32* %right.ptr
    store i32 %right.2, i32* %j.ptr
    %tmp.ptr = alloca i32
    %pivot.ptr = alloca i32
    %left.3 = load i32, i32* %left.ptr
    %right.4 = load i32, i32* %right.ptr
    %buffer5 = add i32 %left.3, %right.4
    %buffer6 = sdiv i32 %buffer5, 2
    %s.7.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 %buffer6
    %struct.str.0.8.ptr = getelementptr inbounds %struct.str, %struct.str* %s.7.ptr, i32 0, i32 0
    %struct.str.0.8.8 = load i32, i32* %struct.str.0.8.ptr
    store i32 %struct.str.0.8.8, i32* %pivot.ptr
    br label %lab..0
lab..0:
    %i.10 = load i32, i32* %i.ptr
    %j.11 = load i32, i32* %j.ptr
    %buffer12 = icmp sle i32 %i.10, %j.11
    br i1 %buffer12, label %lab..1, label %lab..2
lab..1:
    br label %lab..3
lab..3:
    %i.13 = load i32, i32* %i.ptr
    %s.14.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 %i.13
    %struct.str.0.15.ptr = getelementptr inbounds %struct.str, %struct.str* %s.14.ptr, i32 0, i32 0
    %struct.str.0.15.15 = load i32, i32* %struct.str.0.15.ptr
    %pivot.17 = load i32, i32* %pivot.ptr
    %buffer18 = icmp slt i32 %struct.str.0.15.15, %pivot.17
    br i1 %buffer18, label %lab..4, label %lab..5
lab..4:
    %i.19 = load i32, i32* %i.ptr
    %buffer20 = add i32 %i.19, 1
    store i32 %buffer20, i32* %i.ptr
    br label %lab..3
lab..5:
    br label %lab..8
lab..8:
    %j.21 = load i32, i32* %j.ptr
    %s.22.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 %j.21
    %struct.str.0.23.ptr = getelementptr inbounds %struct.str, %struct.str* %s.22.ptr, i32 0, i32 0
    %struct.str.0.23.23 = load i32, i32* %struct.str.0.23.ptr
    %pivot.25 = load i32, i32* %pivot.ptr
    %buffer26 = icmp sgt i32 %struct.str.0.23.23, %pivot.25
    br i1 %buffer26, label %lab..9, label %lab..10
lab..9:
    %j.27 = load i32, i32* %j.ptr
    %buffer28 = sub i32 %j.27, 1
    store i32 %buffer28, i32* %j.ptr
    br label %lab..8
lab..10:
    %i.29 = load i32, i32* %i.ptr
    %j.30 = load i32, i32* %j.ptr
    %buffer31 = icmp sle i32 %i.29, %j.30
    br i1 %buffer31, label %lab..13, label %lab..14
lab..13:
    %i.32 = load i32, i32* %i.ptr
    %s.33.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 %i.32
    %struct.str.0.34.ptr = getelementptr inbounds %struct.str, %struct.str* %s.33.ptr, i32 0, i32 0
    %struct.str.0.34.34 = load i32, i32* %struct.str.0.34.ptr
    store i32 %struct.str.0.34.34, i32* %tmp.ptr
    %i.36 = load i32, i32* %i.ptr
    %s.37.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 %i.36
    %struct.str.0.38.ptr = getelementptr inbounds %struct.str, %struct.str* %s.37.ptr, i32 0, i32 0
    %j.39 = load i32, i32* %j.ptr
    %s.40.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 %j.39
    %struct.str.0.41.ptr = getelementptr inbounds %struct.str, %struct.str* %s.40.ptr, i32 0, i32 0
    %struct.str.0.41.41 = load i32, i32* %struct.str.0.41.ptr
    store i32 %struct.str.0.41.41, i32* %struct.str.0.38.ptr
    %j.43 = load i32, i32* %j.ptr
    %s.44.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 %j.43
    %struct.str.0.45.ptr = getelementptr inbounds %struct.str, %struct.str* %s.44.ptr, i32 0, i32 0
    %tmp.46 = load i32, i32* %tmp.ptr
    store i32 %tmp.46, i32* %struct.str.0.45.ptr
    %i.47 = load i32, i32* %i.ptr
    %buffer48 = add i32 %i.47, 1
    store i32 %buffer48, i32* %i.ptr
    %j.49 = load i32, i32* %j.ptr
    %buffer50 = sub i32 %j.49, 1
    store i32 %buffer50, i32* %j.ptr
    br label %lab..15
lab..14:
    br label %lab..15
lab..15:
    br label %lab..0
lab..2:
    %left.51 = load i32, i32* %left.ptr
    %j.52 = load i32, i32* %j.ptr
    %buffer53 = icmp slt i32 %left.51, %j.52
    br i1 %buffer53, label %lab..18, label %lab..19
lab..18:
    %s.54.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 0
    %left.55 = load i32, i32* %left.ptr
    %j.56 = load i32, i32* %j.ptr
     call void @func.quicksort(%struct.str* %s.54.ptr, i32 %left.55, i32 %j.56)
    br label %lab..20
lab..19:
    br label %lab..20
lab..20:
    %i.58 = load i32, i32* %i.ptr
    %right.59 = load i32, i32* %right.ptr
    %buffer60 = icmp slt i32 %i.58, %right.59
    br i1 %buffer60, label %lab..21, label %lab..22
lab..21:
    %s.61.ptr = getelementptr inbounds %struct.str, %struct.str* %s.ptr, i32 0
    %i.62 = load i32, i32* %i.ptr
    %right.63 = load i32, i32* %right.ptr
     call void @func.quicksort(%struct.str* %s.61.ptr, i32 %i.62, i32 %right.63)
    br label %lab..23
lab..22:
    br label %lab..23
lab..23:
    ret void
}

define i32 @main() {
    %s.ptr = alloca [10 x %struct.str]
    %s.65.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 0
    %struct.str.0.66.ptr = getelementptr inbounds %struct.str, %struct.str* %s.65.ptr, i32 0, i32 0
    store i32 3, i32* %struct.str.0.66.ptr
    %s.67.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 1
    %struct.str.0.68.ptr = getelementptr inbounds %struct.str, %struct.str* %s.67.ptr, i32 0, i32 0
    store i32 1, i32* %struct.str.0.68.ptr
    %s.69.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 2
    %struct.str.0.70.ptr = getelementptr inbounds %struct.str, %struct.str* %s.69.ptr, i32 0, i32 0
    store i32 4, i32* %struct.str.0.70.ptr
    %s.71.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 3
    %struct.str.0.72.ptr = getelementptr inbounds %struct.str, %struct.str* %s.71.ptr, i32 0, i32 0
    store i32 9, i32* %struct.str.0.72.ptr
    %s.73.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 4
    %struct.str.0.74.ptr = getelementptr inbounds %struct.str, %struct.str* %s.73.ptr, i32 0, i32 0
    store i32 2, i32* %struct.str.0.74.ptr
    %s.75.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 5
    %struct.str.0.76.ptr = getelementptr inbounds %struct.str, %struct.str* %s.75.ptr, i32 0, i32 0
    store i32 8, i32* %struct.str.0.76.ptr
    %s.77.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 6
    %struct.str.0.78.ptr = getelementptr inbounds %struct.str, %struct.str* %s.77.ptr, i32 0, i32 0
    store i32 6, i32* %struct.str.0.78.ptr
    %s.79.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 7
    %struct.str.0.80.ptr = getelementptr inbounds %struct.str, %struct.str* %s.79.ptr, i32 0, i32 0
    store i32 7, i32* %struct.str.0.80.ptr
    %s.81.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 8
    %struct.str.0.82.ptr = getelementptr inbounds %struct.str, %struct.str* %s.81.ptr, i32 0, i32 0
    store i32 5, i32* %struct.str.0.82.ptr
    %s.83.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 9
    %struct.str.0.84.ptr = getelementptr inbounds %struct.str, %struct.str* %s.83.ptr, i32 0, i32 0
    store i32 10, i32* %struct.str.0.84.ptr
    %buffer85 = getelementptr inbounds [8 x i8], [8 x i8]* @.str.3, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer85)
    %count.ptr = alloca i32
    store i32 0, i32* %count.ptr
    br label %lab..24
lab..24:
    %count.86 = load i32, i32* %count.ptr
    %buffer87 = icmp slt i32 %count.86, 10
    br i1 %buffer87, label %lab..25, label %lab..26
lab..25:
    %count.88 = load i32, i32* %count.ptr
    %s.89.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 %count.88
    %struct.str.0.90.ptr = getelementptr inbounds %struct.str, %struct.str* %s.89.ptr, i32 0, i32 0
    %struct.str.0.90.90 = load i32, i32* %struct.str.0.90.ptr
    %buffer93 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.4, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer93, i32 %struct.str.0.90.90)
    %count.94 = load i32, i32* %count.ptr
    %buffer95 = add i32 %count.94, 1
    store i32 %buffer95, i32* %count.ptr
    br label %lab..24
lab..26:
    %s.96.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 0
     call void @func.quicksort(%struct.str* %s.96.ptr, i32 0, i32 9)
    %buffer98 = getelementptr inbounds [8 x i8], [8 x i8]* @.str.5, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer98)
    store i32 0, i32* %count.ptr
    br label %lab..29
lab..29:
    %count.99 = load i32, i32* %count.ptr
    %buffer100 = icmp slt i32 %count.99, 10
    br i1 %buffer100, label %lab..30, label %lab..31
lab..30:
    %count.101 = load i32, i32* %count.ptr
    %s.102.ptr = getelementptr inbounds [10 x %struct.str], [10 x %struct.str]* %s.ptr, i32 0, i32 %count.101
    %struct.str.0.103.ptr = getelementptr inbounds %struct.str, %struct.str* %s.102.ptr, i32 0, i32 0
    %struct.str.0.103.103 = load i32, i32* %struct.str.0.103.ptr
    %buffer106 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.6, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer106, i32 %struct.str.0.103.103)
    %count.107 = load i32, i32* %count.ptr
    %buffer108 = add i32 %count.107, 1
    store i32 %buffer108, i32* %count.ptr
    br label %lab..29
lab..31:
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [7 x i8] c"Input:\00", align 1
    @.str.2 = private unnamed_addr constant [7 x i8] c"Result\00", align 1
@.str.3 = private unnamed_addr constant [8 x i8] c"Input:\0A\00", align 1
    @.str.4 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
    @.str.5 = private unnamed_addr constant [8 x i8] c"Result\0A\00", align 1
    @.str.6 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
